#!/usr/bin/env python

import copy

import tiles
import pickups

cdef class AiNode #forward declaration

cdef class Node:
    """An abstract node used in PredictionTree.

    public members:
    - generation: the generation of this node
    - parent: this nodes parent
    """

    cdef int generation
    cdef readonly AiNode smartnode
    cdef Node parent
    cdef object childeren
    cdef float _best_score
    cdef float score
        
    def __init__( self, AiNode smartnode, Node parent = None ):
        self.smartnode = smartnode
        self.parent = parent
        self.childeren = None
        self._best_score = -999

        if parent is not None:
            self.generation = parent.generation+1
        else:
            self.generation = 0

    cdef object generate_childeren( Node self ):
        """Generate and return the list of childeren nodes of this node
        """
        childeren = self.smartnode._generate_childeren()

        self.childeren = []
        for child in childeren:
            self.childeren.append( Node(child, self) )
        
        return self.childeren

    cdef int get_generation( Node self, Node ancestor_node ):
        """Return the amount of generations to its ancestor.

        Returns -1 if the given ancestor is not an ancestor
        """
        cdef int generation
        cdef Node node_it
        
        generation = 0
        node_it = self
        while node_it is not None and node_it is not ancestor_node:
            node_it = node_it.parent
            generation = generation + 1

        if node_it is None:
            generation = -1

        return generation

    # used externally!!!!
    def get_childeren( self ):
        return self.childeren

    cdef float calc_score( Node self ):
        """Return the individual score of this node
        """
        return self.smartnode._calc_score(self.generation)

    cdef float get_total_score( Node self ):
        """Return the total score (parentscores+self) of this node
        """
        cdef Node node
        cdef float total_score
        cdef int i
        
        scores = []
        node = self
        total_score = 0
        i = 0
        while node is not None:
            i = i + 1
            
            total_score = total_score + node.score * i
            node = node.parent

        return total_score / i
    
    cdef void set_score( Node self, float score ):
        """Set the score of this node, and possibly update other nodes in its path.

        Other nodes are only updated if this node didn't have best score, or
        when it's a leaf node.
        """
        self.score = score
        
        # handle best score
        if self.is_leaf() or self._best_score == -999:
            self._best_score = self.get_total_score()
            if self.parent is not None:
                self.parent._recalc_best_score()

    cdef void _recalc_best_score( Node self ):
#        assert self.childeren is not None and len(self.childeren) > 0, "Only childeren call this function, so they must exist"

        cdef Node child
        cdef float old_score        
        
        old_score = self._best_score

        self._best_score = -999
        for child in self.childeren:
            if self._best_score == -999 or \
               child._best_score > self._best_score:
                self._best_score = child._best_score

        if self._best_score <> old_score and \
           self.parent is not None:
            self.parent._recalc_best_score()                    

    # used externally!!!
    def get_best_score( self ):
        """Return the highest score that this node can reach.
        """
        return self._best_score
        
    # used externally!!!
    def get_score( self ):
        return self.score
        
    def get_best_childs( self ):
        cdef Node child, best_child
        
        if self.childeren is None:
            return []

        best_childs = []
        for child in self.childeren:
            best_child = None
            if len(best_childs) > 0:
                best_child = best_childs[0]
                
            if len(best_childs)==0 or child._best_score > best_child._best_score:
                best_childs = [child]
            elif child._best_score == best_child._best_score:
                best_childs.append( child )

        return best_childs

    cdef char is_leaf( Node self ):
        return (self.childeren is None) or (len( self.childeren ) == 0)

cdef enum:
    CYCLES_PER_UPDATE = 256*4
    
cdef class PredictionTree:
    """A tree structure that contains all possible future moves with scores.

    Public members:
    - root_node: the root node of this tree
    - total_generations: the total generations of this tree
    """

    cdef readonly Node root_node
    cdef readonly int total_generations
    cdef readonly object generations
    cdef int MAX_NODES
    cdef int CYCLES_PER_UPDATE
    cdef readonly object nodes_calc
    cdef object leafs
    cdef int node_cnt

    def __init__( self, int MAX_NODES = 256*2, int CYCLES_PER_UPDATE = 256 ):
        self.root_node = None
        self.total_generations = 0
        self.generations = []
        self.MAX_NODES = MAX_NODES
        self.nodes_calc = None
        self.CYCLES_PER_UPDATE = CYCLES_PER_UPDATE
        self.node_cnt = 0

        
    def update( self ):
        """Update the tree as much as possible, using CYCLES_PER_UPDATE as upper limit.
        """
        cdef int cycles_left
        
        if self.root_node is not None:
            cycles_left = self.CYCLES_PER_UPDATE*2/3 # We make sure we calculate all in limited time
            cycles_left = self._update_tree( cycles_left )
            
            cycles_left = cycles_left + self.CYCLES_PER_UPDATE*1/3
            cycles_left = self._calc_nodes_scores( cycles_left )
            
            self._update_tree( cycles_left )

    def set_root( self, Node node ):        
        """Change the root node in an optimized way.

        If the node equals a child of the current root, then the current tree is
        reused.
        """
        cdef char found
        cdef Node child
        
        found = False
        # first try one of its childeren
        if self.root_node is not None:
            for child in self.root_node.childeren:
                if child.smartnode.equals(node.smartnode):
                    found = True
                    self.root_node = child
                    self.root_node.parent = None
                    self.total_generations = self.total_generations - 1
                    self.nodes_calc = [self.root_node] # Recalculate scores of nodes
                
        if not found:
##            print "recalc",
            self.root_node = node
            self.leafs = [self.root_node]
            self.total_generations = 0
            self.nodes_calc = [self.root_node] # Recalculate scores of nodes
##        else:
##            print "norecalc"

        self._update_generations()

    cdef void _update_generations( PredictionTree self ):
        """Update our generation nodes
        """
        assert self.root_node is not None, "Don't call this when root_node is None"

        cdef Node node

        self.generations = []
        self.node_cnt = 0

        generation = [self.root_node]
        while len( generation ) > 0:
            next_generation = []
            for node in generation:
                self.node_cnt = self.node_cnt + 1
                node.generation = len( self.generations )
                childeren = node.childeren
                if childeren is not None:
                    next_generation.extend( childeren )
                
            self.generations.append( generation )
            generation = next_generation

    cdef _update_tree( PredictionTree self, int cycles_left ):
        """Update the tree until the maximum of generations is reached.
        """
        cdef Node node
        
        assert self.root_node is not None, "Don't call this when root_node is None"
        
        while self.node_cnt < self.MAX_NODES and \
              len(self.leafs) > 0 and \
              cycles_left > 0:
            cycles_left = cycles_left - 1

            node = self.leafs.pop(0)
##            node.set_score( node.calc_score() )
            gen = node.get_generation( self.root_node )
            if gen <> -1: # else it's a leaf of old root_node
                self.total_generations = gen - 1
                nodes = node.generate_childeren()
                self.node_cnt = self.node_cnt + len(nodes)
                self.leafs.extend( nodes )

                node.generation = gen
                self.get_nodes_of_generation( gen+1 ).extend( nodes )

        return cycles_left

    cdef _calc_nodes_scores( PredictionTree self, int cycles_left ):
        """Calculate the score of the nodes that aren't calculated yet.
        """
        assert self.root_node is not None, "Don't call this when root_node is None"

        cdef Node node

        if len( self.nodes_calc ) == 0:
            self.nodes_calc = [self.root_node]
            
        while len(self.nodes_calc) > 0 and \
              cycles_left > 0:
            cycles_left = cycles_left - 1
            
            node = self.nodes_calc.pop(0)
            node.set_score( node.calc_score() )

            childeren = node.childeren
            if childeren is not None:
                self.nodes_calc.extend( childeren )
##            else:
##                self.nodes_calc.append( node )
                                
        return cycles_left
        
    def get_nodes_of_generation( self, gen ):
        """Return all the nodes of the generation.
        """
        if gen is not None and gen > -1 and gen < len( self.generations ):
            return self.generations[ gen ]
        else:
            return []
        

class PlayfieldState:
    
    def __init__( self, playfield ):
        self.playfield = playfield

        self.pickups = []
        for tile in self.playfield.level.tiles:
            if tile.pickup is not None:
                self.pickups.append( [tile, tile.pickup] )

    def reset( self ):
        self.pickups = []
        for tile in self.playfield.level.tiles:
            if tile.pickup is not None:
                self.pickups.append( [tile, tile.pickup] )
        
    def get_pickup( self, tile ):
#        self.reset() # FIXME: remove me and work with real playfieldstate
        for (t, pickup) in self.pickups:
            if tile is t:
                return pickup
            
        return None

    def remove_pickup( self, tile ):
        remove_index = None
        i = 0
        for (t, pickup) in self.pickups:
            if tile is t:
                remove_index = i
            i = i + 1

        if remove_index is not None:
            del self.pickups[remove_index]

    def clone( self ):
        clone = PlayfieldState( self.playfield )
        clone.pickups = copy.copy( self.pickups )
        return clone


def AiNode_create( goldcarstate, trailnode = None ):
    self = AiNode( None )

    self.trailnode = trailnode
    self.carstate = goldcarstate
    self.playfieldstate = None
    self.other_trees = None

    return self


cdef class AiNode:

    cdef readonly AiNode parent
    cdef object childeren
    cdef public object trailnode
    cdef public object carstate
    cdef public object playfieldstate
    cdef public object other_trees
    
    def __init__( self, parent ):
        """Creates a new instance when a parent is known.

        When parent is unknown, use static method 'create'.
        """
        self.parent = parent

    cdef object _generate_childeren( AiNode self ):
        """Generate and return the list of childeren nodes of this node
        """
        childeren = []
        trailnodes = self.trailnode.get_out_nodes()
        for n in trailnodes:
            node = AiNode( self )

            node.carstate       = self.carstate
            node.playfieldstate = self.playfieldstate
            node.other_trees  = self.other_trees
            
            node.trailnode = n
            childeren.append( node )
            
        return childeren

    def set_playfield( self, playfield ):
        self.playfieldstate = PlayfieldState( playfield )
        
    def set_other_trees( self, other_trees ):
        self.other_trees = other_trees

        # Optimization: only look at tree of main player, ignore rest
##        if len(self.other_trees) > 1:
##            self.other_trees = [self.other_trees[0]]

        
    cdef float _calc_score( AiNode self, int distance ):
        cdef AiNode node
        cdef float score
        
        if self.parent is not None:
            self.playfieldstate = self.parent.playfieldstate
            self.carstate = self.parent.carstate

        node = self

        if node.playfieldstate is None:
            print "playfieldstate shouldn't be None in real game"
            return 0

        score = 0

        if isinstance(node.trailnode.tile, tiles.Enterance):
            if isinstance( node.carstate.collectible, pickups.Diamond ):                
                node.carstate = copy.copy( node.carstate )
                node.carstate.collectible = None
                score = score + 2

        score = score + self._calc_tile_pickups( node )
        score = score + self._calc_other_cars( node, distance )

        return score

    cdef float _calc_tile_pickups( AiNode self, AiNode node ):
        cdef float score
        
        score = 0
        
        if node.playfieldstate.get_pickup( node.trailnode.tile ) <> None:
            if isinstance(node.trailnode.tile.pickup, pickups.CopperCoin):
                score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.GoldBlock):
                if isinstance( node.carstate.collectible, pickups.Axe ):
                    score = 1
                else:
                    score = 0.1
            elif isinstance(node.trailnode.tile.pickup, pickups.RockBlock):
                 score = -1
            elif isinstance(node.trailnode.tile.pickup, pickups.Diamond):
                if not isinstance( node.carstate.collectible, pickups.Diamond ):
                    score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Dynamite):
                 score = -8
            elif isinstance(node.trailnode.tile.pickup, pickups.Lamp):
                 score = 5
            elif isinstance(node.trailnode.tile.pickup, pickups.Axe):
                 score = 2
            elif isinstance(node.trailnode.tile.pickup, pickups.Flag):
                 if self.carstate.goldcar.nr == node.trailnode.tile.pickup.goldcar.nr:
                     score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Leprechaun):
                 score = -2
            elif isinstance(node.trailnode.tile.pickup, pickups.Torch):
                 score = 0
            elif isinstance(node.trailnode.tile.pickup, pickups.Key):
                 score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Mirror):
                 score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Oiler):
                 score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Multiplier):
                 score = 1
            elif isinstance(node.trailnode.tile.pickup, pickups.Balloon):
                 score = 0
            elif isinstance(node.trailnode.tile.pickup, pickups.Ghost):
                 score = 1
            
            if isinstance( node.trailnode.tile.pickup, pickups.Collectible ):
                node.carstate = copy.copy( node.carstate )
                node.carstate.collectible = node.trailnode.tile.pickup
            elif isinstance( node.trailnode.tile.pickup, pickups.PowerUp ):
                node.carstate = copy.copy( node.carstate )
                node.carstate.modifier = node.trailnode.tile.pickup
            
            node.playfieldstate = node.playfieldstate.clone()
            node.playfieldstate.remove_pickup( node.trailnode.tile )

        return score

    cdef float _calc_other_cars( AiNode self, AiNode node, int distance ):
        cdef float score
        cdef Node ai_node
        cdef AiNode othernode
        
        score = 0

        for tree in self.other_trees:
            gen_nodes = tree.get_nodes_of_generation( distance )
            for ai_node in gen_nodes:
                othernode = ai_node.smartnode
                if node.trailnode.tile is othernode.trailnode.tile:
                    if othernode.carstate.goldcar.collectible is not None:
                        if othernode.carstate.goldcar.collectible.is_good():
                            score = score + 5.0 / len( gen_nodes ) /  max(distance, 1)
                        elif othernode.carstate.goldcar.collectible.is_bad():
                            score = score - 5.0 / len( gen_nodes ) /  max(distance, 1)
                    if node.carstate.goldcar.collectible is not None:
                        if node.carstate.goldcar.collectible.is_good():
                            score = score - 5.0 / len( gen_nodes ) /  max(distance, 1)
                        elif node.carstate.goldcar.collectible.is_bad():
                            score = score + 5.0 / len( gen_nodes ) /  max(distance, 1)

                # Calc parent node when crossing (can pass by)
                if node.parent is not None and\
                   node.parent.trailnode.tile is othernode.trailnode.tile and\
                   node.parent.trailnode.in_dir != othernode.trailnode.in_dir:
                    if othernode.carstate.goldcar.collectible is not None:
                        if othernode.carstate.goldcar.collectible.is_good():
                            score = score + 5.0 / len( gen_nodes ) /  max(distance, 1)
                        elif othernode.carstate.goldcar.collectible.is_bad():
                            score = score - 5.0 / len( gen_nodes ) /  max(distance, 1)
                    if node.parent.carstate.goldcar.collectible is not None:
                        if node.parent.carstate.goldcar.collectible.is_good():
                            score = score - 5.0 / len( gen_nodes ) /  max(distance, 1)
                        elif node.parent.carstate.goldcar.collectible.is_bad():
                            score = score + 5.0 / len( gen_nodes ) /  max(distance, 1)
                        
        return score

    cdef int equals( AiNode self, AiNode other ):
        """Used for updating root node in tree to one of it's childeren.
        """
        return self.trailnode.tile is other.trailnode.tile and \
               self.trailnode.in_dir.__eq__(other.trailnode.in_dir)

    def nequals( self, other ):
        return not self.equals(other)

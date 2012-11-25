#!/usr/bin/env python

import monorail.ai as ai

class SimpleNode (ai.Node):
    """AiNode for use in the unit tests
    """
    def __init__( self, parent = None ):
        ai.Node.__init__( self, parent )

    def generate_childeren( self ):
        """Generate and return the list of childeren nodes of this node
        """
        self.childeren = [SimpleNode(self), SimpleNode(self)]
        return self.childeren

    def calc_score( self ):
        """Return the individual score of this node
        """
        return 1

    def __eq__( self, other ):
        return self is other

##class TestNode:
##    def test_get_generation( self ):
##        """Given a node
##        When childeren and grandchilderen are calculated
##        Then child is generation 1 and grandchild generation 2
##        """
##        # Given
##        node = SimpleNode()
##        
##        # When
##        child = node.generate_childeren()[0]
##        grandchild = child.generate_childeren()[0]
##                
##        # Then
##        assert node.get_generation( node ) == 0
##        assert child.get_generation( node ) == 1
##        assert grandchild.get_generation( node ) == 2
##        assert node.get_generation( grandchild ) == -1

##    def test_set_score_propagates_to_parent_best_score( self ):
##        """Given a structure of child Nodes
##        When the score is set to high on a child
##        Then the best_score of the parents are updated
##        """            
##        # Given
##        node = SimpleNode()
##
##        node.generate_childeren()
##        node.set_score(1)
##        for child in node.get_childeren():
##            child.generate_childeren()        
##            child.set_score(1)
##
##        # When/Then
##        child = node.get_childeren()[1].get_childeren()[0]
##        child.set_score(3)
##        assert node.get_best_score() == child.get_total_score()
##        assert 1 < node.get_best_score() < 5
##
##        child = node.get_childeren()[0].get_childeren()[0]
##        child.set_score( 5 )
##        assert node.get_best_score() == child.get_total_score()
##        best_score = node.get_best_score()
##
##        child = node.get_childeren()[1].get_childeren()[0]
##        child.set_score(3)
##        assert node.get_best_score() == best_score

##    def test_get_best_child( self ):
##        """Given a structure of child nodes
##        When the score of one child is higher than another
##        Then get_best_childs returns the child with the highest score
##        """
##        # Given
##        node = SimpleNode()
##
##        node.generate_childeren()
##        node.set_score(1)
##        for child in node.get_childeren():
##            child.set_score(1)
##            
##        # When/Then
##        assert len(node.get_best_childs()) == 2
##
##        child = node.get_childeren()[1]
##        child.set_score(3)
##
##        assert len(node.get_best_childs()) == 1
##        assert node.get_best_childs()[0] is child

##    def test_is_leaf( self ):
##        """Given a structure of child nodes
##        When is_leaf is called on a node
##        It returns true when the node is a leaf, and false otherwise
##        """
##        # Given
##        node = SimpleNode()
##
##        node.generate_childeren()
##        for child in node.get_childeren():
##            child.generate_childeren()
##            
##        # When/Then
##        assert not node.is_leaf()
##        assert not node.get_childeren()[0].is_leaf()
##        assert node.get_childeren()[0].get_childeren()[0].is_leaf()

class TestPredictionTree:
    def test_constructor( self ):
        tree = ai.PredictionTree()
        tree = ai.PredictionTree( 30 )

    def test_set_root_sets_root( self ):
        """Given a PredictionTree and a node
        When set_root is called with the node
        Then root_node is set to that node
        """
        # Given
        tree = ai.PredictionTree()
        node = SimpleNode()

        # When
        tree.set_root( node )

        # Then
        assert tree.root_node is node

##    def test_update_creates_childeren( self ):
##        """Given a PredictionTree with a root node
##        When update is called
##        Then the childeren of the root node are recursively calculated
##        """
##        # Given
##        tree = ai.PredictionTree()
##        tree.set_root( SimpleNode() )
##
##        # When
##        tree.update()
##
##        # Then
##        assert tree.root_node.get_childeren() is not None
##        assert len(tree.root_node.get_childeren()) == 2
##
##        child = tree.root_node.get_childeren()[0]
##        assert child is not None
##        assert len(child.get_childeren()) == 2
        

##    def test_replace_root_with_child_is_optimized( self ):
##        """Given a PredictionTree with root node and childeren
##        When the root node is replaced by one of its childs
##        The tree is reused
##        """
##        # Given
##        tree = ai.PredictionTree()
##        tree.set_root( SimpleNode() )
##        tree.update() # generate the tree
##        
##        # When
##        tree.set_root( tree.root_node.get_childeren()[0] )
##        
##        # Then
##        assert len(tree.root_node.get_childeren()) == 2

##    def test_replace_root_with_non_child( self ):
##        """Given a PredictionTree with root node and childeren
##        When the root node is replaced by a new node
##        The tree is created from scratch
##        """
##        # Given
##        tree = ai.PredictionTree()
##        tree.set_root( SimpleNode() )
##        tree.update() # generate the tree
##        
##        # When
##        tree.set_root( SimpleNode() )
##        
##        # Then
##        assert tree.root_node.get_childeren() is None

##    def test_scores_are_calculated( self ):
##        """Given a PredictionTree with root node
##        When the childeren are calculated
##        Then all nodes receive scores
##        """
##        # Given
##        tree = ai.PredictionTree( MAX_GENERATIONS = 5 )
##        tree.set_root( SimpleNode() )
##        
##        # When
##        tree.update()
##        
##        # Then
##        child = tree.root_node.get_childeren()[0]
##        grandchild = child.get_childeren()[0]
##        
##        assert tree.root_node.get_total_score() == 1
##        assert 1 < child.get_total_score() < grandchild.get_total_score() < 3
        
##    def test_scores_are_recalculated_on_root_change( self ):
##        """Given a PredictionTree with root node and scores
##        When the root node changes to a child node
##        Then all node scores are recalculated
##        """
##        # Given
##        tree = ai.PredictionTree( MAX_GENERATIONS = 5 )
##        tree.set_root( SimpleNode() )
##        
##        # When
##        tree.update()
##        tree.set_root( tree.root_node.get_childeren()[0] )
##        tree.update()
##        
##        # Then
##        child = tree.root_node.get_childeren()[0]
##        grandchild = child.get_childeren()[0]
##        
##        assert tree.root_node.get_total_score() == 1
##        assert 1 < child.get_total_score() < grandchild.get_total_score() < 3
        
##    def test_get_nodes_of_generation( self ):
##        """Given a PredictionTree with root node and childeren
##        When the childeren are calculated
##        Then we can get the nodes of each generation
##        """
##        # Given
##        tree = ai.PredictionTree( MAX_GENERATIONS = 5 )
##        tree.set_root( SimpleNode() )
##        
##        # When
##        tree.update()
##        
##        # Then
##        generation = tree.get_nodes_of_generation(0)
##        assert len(generation) == 1
##        assert generation[0] is tree.root_node
##        assert generation[0].generation == 0
##
##        generation = tree.get_nodes_of_generation(1)
##        assert len(generation) == 2
##        assert generation[0] in tree.root_node.get_childeren()
##        assert generation[1] in tree.root_node.get_childeren()
##        assert generation[0].generation == 1
##        assert generation[0].generation == 1
##                
##        generation = tree.get_nodes_of_generation(2)
##        assert len(generation) == 4
##        assert generation[0] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[0] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[1] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[1] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[2] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[2] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[3] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[3] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[0].generation == 2
##        assert generation[1].generation == 2
##        assert generation[2].generation == 2
##        assert generation[3].generation == 2
                
##    def test_get_nodes_of_generation_on_new_root( self ):
##        """Given a PredictionTree with root node and childeren
##        When root node is recalculated
##        Then the generations are also recalculated
##        """
##        # Given
##        tree = ai.PredictionTree( MAX_GENERATIONS = 5 )
##        tree.set_root( SimpleNode() )
##        
##        # When
##        tree.update()
##        tree.set_root( tree.root_node.get_childeren()[0] )
##        tree.update()
##        
##        # Then
##        generation = tree.get_nodes_of_generation(0)
##        assert len(generation) == 1
##        assert generation[0] is tree.root_node
##        assert generation[0].generation == 0
##
##        generation = tree.get_nodes_of_generation(1)
##        assert len(generation) == 2
##        assert generation[0] in tree.root_node.get_childeren()
##        assert generation[1] in tree.root_node.get_childeren()
##        assert generation[0].generation == 1
##        assert generation[0].generation == 1
##                
##        generation = tree.get_nodes_of_generation(2)
##        assert len(generation) == 4
##        assert generation[0] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[0] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[1] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[1] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[2] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[2] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[3] in tree.root_node.get_childeren()[0].get_childeren()\
##               or generation[3] in tree.root_node.get_childeren()[1].get_childeren()
##        assert generation[0].generation == 2
##        assert generation[1].generation == 2
##        assert generation[2].generation == 2
##        assert generation[3].generation == 2
##                

#!/usr/bin/env python

from source.koon.geo import Vec3D
from source.world import *
from source.tiles import *
import source.control as ctrl
import source.ai as ai

class TestGroundControl:

    def test_init( self ):
        ground_control = ctrl.GroundControl( None )

    def test_update_prediction_trees( self ):
        playfield = Playfield()
        playfield.load("tests/levelTest.lvl")

        tile = playfield.level.get_first_flat_tile()
        goldcar = GoldCar( TrailPosition(tile, 0), 0 )
        playfield.goldcars = [goldcar]

        ground_control = ctrl.GroundControl( playfield )
        ground_control.add_controllers( [ctrl.AiController( goldcar )] )

        ground_control._update_prediction_trees()

##    def test_tree_reuse_on_root_change( self ):
##        """Given a PredictionTree with root AiNode and scores
##        When the root node changes to an AiNode with same position as child node
##        Then the tree structure is reused
##        """
##        # Given
##        playfield = Playfield()
##        playfield.load("tests/levelTest.lvl")
##
##        tile = playfield.level.get_first_flat_tile()
##
##        pos = TrailPosition(tile, 0)
##
##        tree = ai.PredictionTree()
##        tree.set_root( ctrl.AiNode.create(None, tile, pos.get_in_direction()) )
##        
##        # When
##        tree.update()
##        child = tree.root_node.get_childeren()[0]
##        grandchild = child.get_childeren()[0]
##
##        child_copy = ctrl.AiNode.create( None, child.trailnode.tile, child.trailnode.in_dir )        
##        tree.set_root( child_copy )
##        
##        # Then        
##        assert tree.root_node.get_childeren()[0] is grandchild
            
        
class TestPlayfieldState:

    def test_init( self ):
        playfield = Playfield()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(0,1,0), Tile.Type.FLAT ) )

        playfieldstate = ai.PlayfieldState( playfield )

    def test_get_remove_pickup( self ):
        # Given
        playfield = Playfield()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(0,1,0), Tile.Type.FLAT ) )

        pickup = CopperCoin()
        playfield.level.get_tile(0, 0).pickup = pickup
        
        # When
        playfieldstate = ai.PlayfieldState( playfield )
        
        # Then
        assert playfieldstate.get_pickup( playfield.level.get_tile(0,0) ) is pickup
        assert playfieldstate.get_pickup(playfield.level.get_tile(0,1) ) is None

        # And when
        playfieldstate.remove_pickup( playfield.level.get_tile(0,0) )

        # Then
        assert playfieldstate.get_pickup( playfield.level.get_tile(0,0) ) is None

    def test_clone( self ):
        # Given
        playfield = Playfield()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(0,1,0), Tile.Type.FLAT ) )

        pickup = CopperCoin()
        playfield.level.get_tile(0, 0).pickup = pickup
        playfieldstate = ai.PlayfieldState( playfield )
        
        # When
        clone = playfieldstate.clone()

        # Then
        assert clone.playfield is playfieldstate.playfield
        assert clone.pickups is not playfieldstate.pickups
        

class TestGoldcarNodeState:
    def test_init( self ):
        tile = Tile( Vec3D(), Tile.Type.FLAT )
        node = ctrl.GoldcarNodeState( GoldCar( TrailPosition( tile, 0 ), 0 ) )

##class TestAiNode:
##    def test_out_nodes_contain_same_members( self ):
##        # Given
##        center = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        west   = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##        center.set_neighbor( south, Direction.SOUTH )
##        center.set_neighbor( west, Direction.WEST )
##        south.set_neighbor( center, Direction.NORTH )
##        west.set_neighbor( center, Direction.EAST )
##
##        carstate = ctrl.GoldcarNodeState( GoldCar( TrailPosition( center, 0 ), 0 ) )
##        ai_node = ctrl.AiNode.create( carstate, center, Direction.SOUTH )
##
##        playfield = Playfield()
##        ai_node.set_playfield( playfield )
##
##        # When
##        ai_node.score = 99
##        out = ai_node.generate_childeren()[0]
##
##        # Then
##        assert out.trailnode.tile is west
##        assert out.playfieldstate is ai_node.playfieldstate
##        assert out.carstate is ai_node.carstate

##    def test_get_generation( self ):
##        # Given
##        center = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south2 = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        west   = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##        west2  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##        center.set_neighbor( south, Direction.SOUTH )
##        center.set_neighbor( west, Direction.WEST )
##        south.set_neighbor( center, Direction.NORTH )
##        south.set_neighbor( south2, Direction.SOUTH )
##        west.set_neighbor( center, Direction.EAST )
##        west.set_neighbor( west2, Direction.WEST )
##        south2.set_neighbor( south, Direction.NORTH )
##        west2.set_neighbor( west, Direction.EAST )        
##        
##        # When
##        carstate = ctrl.GoldcarNodeState( GoldCar( TrailPosition( center, 0 ), 0 ) )
##        ai_node = ctrl.AiNode.create( carstate, center, Direction.NORTH )
##        
##        # Then
##        assert ai_node.get_generation( ai_node ) == 0
##
##        # First generation
##        nodes1 = ai_node.generate_childeren()
##        assert len(nodes1) == 2
##        assert nodes1[0].get_generation( nodes1[0] ) == 0
##        assert nodes1[0].get_generation( ai_node )   == 1
##
##        assert nodes1[1].get_generation( nodes1[1] ) == 0
##        assert nodes1[1].get_generation( ai_node )   == 1
##
##        # Second generation
##        nodes2 = nodes1[0].generate_childeren()
##        assert len(nodes2) == 1
##        assert nodes2[0].get_generation( nodes2[0] ) == 0
##        assert nodes2[0].get_generation( nodes1[0] ) == 1
##        assert nodes2[0].get_generation( ai_node )   == 2


##    def test_set_score_propagates_to_parent_max_score( self ):
##        # Given
##        center = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south2 = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        west   = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##        west2  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##        center.set_neighbor( south, Direction.SOUTH )
##        center.set_neighbor( west, Direction.WEST )
##        south.set_neighbor( center, Direction.NORTH )
##        south.set_neighbor( south2, Direction.SOUTH )
##        west.set_neighbor( center, Direction.EAST )
##        west.set_neighbor( west2, Direction.WEST )
##        south2.set_neighbor( south, Direction.NORTH )
##        west2.set_neighbor( west, Direction.EAST )        
##
##        # When
##        carstate = ctrl.GoldcarNodeState( GoldCar( TrailPosition( center, 0 ), 0 ) )
##        ai_node = ctrl.AiNode.create( carstate, center, Direction.NORTH )
##
##        ai_node.generate_childeren()
##        for child in ai_node.get_childeren():
##            child.generate_childeren()
##            
##        # Then
##        ai_node.get_childeren()[1].get_childeren()[0].set_total_score(3)
##        assert ai_node.get_best_score() == 3
##
##        ai_node.get_childeren()[0].set_total_score( 5 )
##        assert ai_node.get_best_score() == 5
##
##        ai_node.get_childeren()[1].get_childeren()[0].set_total_score(3)
##        assert ai_node.get_best_score() == 5
##        
##        ai_node.get_childeren()[1].get_childeren()[0].set_total_score(7)
##        assert ai_node.get_best_score() == 7
        
class TestAiController:

    def test_( self ):
        """Given a goldcar with a diamond
           When there is a path to an enterance
           Then AI switches trails to enterance"""
        # Give
        # When
        # Then


##class TestPredictionTree:
##    def test_update( self ):
##        playfield = Playfield()
##        playfield.load("tests/levelTest.lvl")
##
##        tile = playfield.level.get_first_flat_tile()
##        goldcar = GoldCar( TrailPosition(tile, 0), 0 )
##
##        prediction_tree = PredictionTree( goldcar, playfield )
##
##        prediction_tree.update()
##        print "gen", prediction_tree.total_generations
##
##        print "score", prediction_tree.root_node.get_childeren()[0].score        
##

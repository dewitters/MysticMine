#!/usr/bin/env python

import os

from source.tiles import *
from source.koon.geo import Vec3D

class TestDirection:

    def test_dirs( self ):
        a = Direction.NORTH
        b = Direction.SOUTH
        assert not (a == b)
        assert a <> b
        a = b
        assert a == b

    def test_opposite( self ):
        a = Direction.WEST
        assert a.get_opposite() == Direction.EAST
        assert a.get_opposite().get_opposite() == a

class TestTileAndTrail:
    
    def test_constructors( self ):
        t = Tile( Vec3D( -1, 3, 0 ), Tile.Type.SOUTH_SLOPE_TOP, Trail.Type.HILL )
        assert t.pos == Vec3D( -1, 3, 0 )
        assert t.type == Tile.Type.SOUTH_SLOPE_TOP

        t = Tile( Vec3D( -1, 3, 0 ), Tile.Type.SOUTH_SLOPE_TOP )

        t = Tile( Vec3D(0,1,0), Tile.Type.SOUTH_SLOPE_TOP )
        assert t.trail.type == Trail.Type.HILL

    def test_get_length( self ):
        flat = Tile( Vec3D(), Tile.Type.FLAT )
        hill = Tile( Vec3D(), Tile.Type.NORTH_SLOPE_TOP )

        assert hill.get_length() > flat.get_length()
        

    def test_neighbors( self ):
        top   = Tile( Vec3D(0,0,0), Tile.Type.FLAT, Trail.Type.SW )
        left  = Tile( Vec3D(0,0,0), Tile.Type.FLAT, Trail.Type.SE )
        right = Tile( Vec3D(0,0,0), Tile.Type.FLAT, Trail.Type.NW )

        top.set_neighbor( right, Direction.SOUTH )
        top.set_neighbor( left, Direction.WEST )
        left.set_neighbor( top, Direction.EAST )
        right.set_neighbor( top, Direction.NORTH )

        assert top.get_in_tile() in [left, right]
        assert top.get_out_tile() in [left, right]
        assert top.get_in_tile() <> top.get_out_tile()

        
    def test_trail_in_out_direction( self ):
        t = Tile( Vec3D(0,0,0), Tile.Type.FLAT, Trail.Type.SE )
        assert t.trail.get_in_direction() in [Direction.EAST, Direction.SOUTH]
        assert t.trail.get_out_direction() in [Direction.EAST, Direction.SOUTH]
        assert t.trail.get_in_direction() <> t.trail.get_out_direction()
        
        t = Tile( Vec3D(0,0,0), Tile.Type.NORTH_SLOPE_TOP ) 
        assert t.trail.get_in_direction() in [Direction.NORTH, Direction.SOUTH]
        assert t.trail.get_out_direction() in [Direction.NORTH, Direction.SOUTH]
        assert t.trail.get_in_direction() <> t.trail.get_out_direction()

    def test_neighbor_offset( self ):
        flat = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        assert flat.get_neighbor_offset( Direction.NORTH ) == Vec3D(0,-1,0)

        slope = Tile( Vec3D(0,0,0), Tile.Type.EAST_SLOPE_BOT )
        assert slope.get_neighbor_offset( Direction.WEST ) == Vec3D(0,-1,0)
        assert slope.get_neighbor_offset( Direction.SOUTH ) == Vec3D(0,0,0)

    def test_is_switch( self ):
        center = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        north  = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        east   = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        west   = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        
        center.set_neighbor( north, Direction.NORTH )
        center.set_neighbor( east, Direction.EAST )
        center.set_neighbor( west, Direction.WEST )
        north.set_neighbor( center, Direction.SOUTH )
        east.set_neighbor( center, Direction.WEST )
        west.set_neighbor( center, Direction.EAST )
        
        assert not north.trail.is_switch()
        assert center.trail.is_switch()

    def test_switch_trail( self ):
        top    = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        left   = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        bottom = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        right  = Tile( Vec3D(0,0,0), Tile.Type.FLAT )

        top.set_neighbor( left, Direction.SOUTH )
        top.set_neighbor( right, Direction.EAST )
        left.set_neighbor( top, Direction.NORTH )
        left.set_neighbor( bottom, Direction.EAST )
        bottom.set_neighbor( left, Direction.WEST )
        bottom.set_neighbor( right, Direction.NORTH )
        right.set_neighbor( top, Direction.WEST )
        right.set_neighbor( bottom, Direction.SOUTH )

        top.trail.switch_it()
        assert top.trail.type == Trail.Type.SE
        left.trail.switch_it()
        assert left.trail.type == Trail.Type.NE
        bottom.trail.switch_it()
        assert bottom.trail.type == Trail.Type.NW
        right.trail.switch_it()
        assert right.trail.type == Trail.Type.SW

    def test_align_switch( self ):
        center = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        center.trail.type = Trail.Type.SE
        north = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        north.trail.type = Trail.Type.NS
        east = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        east.trail.type = Trail.Type.EW
        west = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        west.trail.type = Trail.Type.EW
        
        center.set_neighbor( north, Direction.NORTH )
        center.set_neighbor( east, Direction.EAST )
        center.set_neighbor( west, Direction.WEST )
        north.set_neighbor( center, Direction.SOUTH )
        east.set_neighbor( center, Direction.WEST )
        west.set_neighbor( center, Direction.EAST )
        
        center.trail.align()
        tt = center.trail.type
        assert tt == Trail.Type.NE or tt == Trail.Type.NW or tt == Trail.Type.EW
        center.trail.align()
        assert center.trail.type == tt
        
        center.trail.type = Trail.Type.EW
        center.trail.align( Direction.NORTH )
        tt = center.trail.type
        assert tt == Trail.Type.NE or tt == Trail.Type.NW

    def test_save_load( self ):
        tile1 = Tile( Vec3D(6,5,4), Tile.Type.NORTH_SLOPE_TOP )
        tile2 = Tile( Vec3D(3,4,1), Tile.Type.FLAT )
        tile2.trail.type = Trail.Type.SW

        # save tiles
        f = open( "tilesave", "wb" );
        
        tile1.save( f )
        tile2.save( f )
        
        f.close()

        # load tiles
        f = open( "tilesave", "rb" );
        
        copy1 = Tile.load( f )
        copy2 = Tile.load( f )
        
        assert copy1.type == Tile.Type.NORTH_SLOPE_TOP
        assert copy1.trail.type == Trail.Type.HILL
        assert copy1.pos == Vec3D(6,5,4)
        assert copy2.type == Tile.Type.FLAT
        assert copy2.trail.type == Trail.Type.SW
        assert copy2.pos == Vec3D(3,4,1)
        
        f.close()

        os.remove( "tilesave" )


##    def test_get_set_pickup()
##        CopperCoin gold;
##
##        Tile tile( Vec3D(0,0,0), Tile.Type.FLAT );
##
##        assert tile.get_pickup() == NULL );
##        tile.add_pickup( new CopperCoin() );
##        assert tile.get_pickup() != NULL );
##        tile.remove_pickup();
##        assert tile.get_pickup() == NULL );
##        tile.remove_pickup();
##        assert tile.get_pickup() == NULL );
##
##    void TestTile.Type.test_selected() {
##        Tile tile( Vec3D(0,0,0), Tile.Type.FLAT );
##
##        assert !tile.is_selected() );
##        tile.set_selected( true );
##        assert tile.is_selected() );

class TestEnteranceTile:

    def testInit( self ):
        enterance = Enterance( Vec3D(0,1,2) )

        assert enterance.pos == Vec3D(0,1,2)

    def testGetSetPortal( self ):
        enterances = [ Enterance( Vec3D(0,0,0) ) for i in range(0,3) ]

        enterances[0].set_portals( enterances )

        test = [ False for i in range(0, len(enterances)) ]
        for i in range(0, 20): # Should have received all after 50 tries
            index = enterances.index( enterances[0].get_random_portal() )
            test[ index ] = True

        assert test.count( False ) == 0
            


class TestTrailPosition:

    def setup_class( self ):
        self.tile1 = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        self.tile2 = Tile( Vec3D(0,0,0), Tile.Type.FLAT )

    def test_constructors( self ):
        pos = TrailPosition( self.tile1, 0 )

    def test_move( self ):
        top    = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        left   = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        bottom = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        right  = Tile( Vec3D(0,0,0), Tile.Type.FLAT )

        top.trail.type = Trail.Type.SW
        left.trail.type = Trail.Type.SE
        bottom.trail.type = Trail.Type.NE
        right.trail.type = Trail.Type.NW

        top.set_neighbor( left, Direction.WEST )
        top.set_neighbor( right, Direction.SOUTH )
        left.set_neighbor( top, Direction.EAST )
        left.set_neighbor( bottom, Direction.SOUTH )
        bottom.set_neighbor( left, Direction.NORTH )
        bottom.set_neighbor( right, Direction.EAST )
        right.set_neighbor( top, Direction.NORTH )
        right.set_neighbor( bottom, Direction.WEST )

        pos = TrailPosition( top, top.get_length() / 2 )
        assert pos.tile == top
        pos -= top.get_length()
        assert pos.tile == right
        pos -= right.get_length()
        assert pos.tile == bottom
        pos -= bottom.get_length()
        assert pos.tile == left
        pos -= left.get_length()
        assert pos.tile == top

        pos += top.get_length()
        assert pos.tile == left
        pos += left.get_length()
        assert pos.tile == bottom
        pos += bottom.get_length()
        assert pos.tile == right
        pos += right.get_length()
        assert pos.tile == top

        pos -= 2 * top.get_length()
        assert pos.tile == bottom
        pos -= 5 * top.get_length()
        assert pos.tile == left


        # Test bounce agains wrong trail
        left.trail.type = Trail.Type.NS
        pos.set_position( top, top.get_length() / 2 )
        if pos.is_reversed():
            pos.reverse_progress()
            
        pos += top.get_length()
        assert pos.tile == top

        right.trail.type = Trail.Type.EW
        pos.set_position( top, top.get_length() / 2 )
        pos -= top.get_length()
        assert pos.tile == top

    def test_add_and_sub( self ):
        top    = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        left   = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        bottom = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        right  = Tile( Vec3D(0,0,0), Tile.Type.FLAT )

        top.trail.type = Trail.Type.SW
        left.trail.type = Trail.Type.SE
        bottom.trail.type = Trail.Type.NE
        right.trail.type = Trail.Type.NW

        top.set_neighbor( left, Direction.WEST )
        top.set_neighbor( right, Direction.SOUTH )
        left.set_neighbor( top, Direction.EAST )
        left.set_neighbor( bottom, Direction.SOUTH )
        bottom.set_neighbor( left, Direction.NORTH )
        bottom.set_neighbor( right, Direction.EAST )
        right.set_neighbor( top, Direction.NORTH )
        right.set_neighbor( bottom, Direction.WEST )

        pos = TrailPosition( top, top.get_length() / 2 )
        assert pos.tile == top
        next = pos + top.get_length()
        assert next.tile == left
        assert pos.tile == top
        pos += top.get_length()
        assert pos == next

        pos = TrailPosition( top, top.get_length() / 2 )
        assert pos.tile == top
        next = pos - top.get_length()
        assert next.tile == right
        assert pos.tile == top
        pos -= top.get_length()
        assert pos == next

    def test_to_next_tile( self ):
        center = Tile( Vec3D, Tile.Type.FLAT )
        east   = Tile( Vec3D, Tile.Type.FLAT )
        west   = Tile( Vec3D, Tile.Type.FLAT )

        center.trail.type = Trail.Type.EW
        east.trail.type = Trail.Type.EW
        west.trail.type = Trail.Type.EW

        center.set_neighbor( east, Direction.EAST )
        center.set_neighbor( west, Direction.WEST )
        east.set_neighbor( center, Direction.WEST )
        west.set_neighbor( center, Direction.EAST )
        
        pos = TrailPosition( center, 50 )
        assert pos.tile == center
        pos.to_next_tile()
        assert pos.tile is not None and pos.tile <> center
        pos.reverse_progress()
        pos.to_next_tile()
        assert pos.tile == center
        pos.to_next_tile();
        assert pos.tile is not None and pos.tile <> center

    def test_get_distance( self ):
        center = Tile( Vec3D, Tile.Type.FLAT )
        east   = Tile( Vec3D, Tile.Type.FLAT )

        center.trail.type = Trail.Type.EW
        east.trail.type = Trail.Type.EW

        center.set_neighbor( east, Direction.EAST )
        east.set_neighbor( center, Direction.WEST )

        pos1 = TrailPosition( center, 50 )
        pos2 = TrailPosition( center, 150 )

        assert pos1.get_distance( pos2 ) == 100

        pos2 = TrailPosition( center, 50 )
        pos2 -= center.get_length() + 5

        assert pos2.get_distance( pos1 ) == center.get_length() + 5

class TestTrailNode:
##    def test_next_node( self ):
##        center = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        south  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
##        west   = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
##
##        center.set_neighbor( south, Direction.SOUTH )
##        center.set_neighbor( west, Direction.WEST )
##        south.set_neighbor( center, Direction.NORTH )
##        west.set_neighbor( center, Direction.EAST )
##
##        node = TrailNode( center, None )
##        
##        next = node.get_next_node()
##        assert node.tile == center
##        assert next.tile == south

    def test_get_out_nodes( self ):
        center = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
        south  = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )
        west   = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )

        center.set_neighbor( south, Direction.SOUTH )
        center.set_neighbor( west, Direction.WEST )
        south.set_neighbor( center, Direction.NORTH )
        west.set_neighbor( center, Direction.EAST )

        node = TrailNode( center, None )
        
        outs = node.get_out_nodes()
        assert len(outs) == 2
        assert outs[0].tile in [south, west]
        assert outs[1].tile in [south, west]
        assert outs[0] <> outs[1]

    def test_get_out_nodes_enterance( self ):
        # Given
        enter_a = Enterance( Vec3D() )
        enter_a.trail.type = Trail.Type.EW
        enter_b = Enterance( Vec3D() )
        enter_b.trail.type = Trail.Type.EW
        enter_c = Enterance( Vec3D() )
        enter_c.trail.type = Trail.Type.EW

        tile_b = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )
        tile_c = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.EW )

        enter_b.set_neighbor( tile_b, Direction.WEST )
        enter_c.set_neighbor( tile_c, Direction.WEST )
        tile_b.set_neighbor( enter_b, Direction.EAST )
        tile_c.set_neighbor( enter_c, Direction.EAST )
        
        enter_a.set_portals( [enter_b, enter_c] )

        # When
        node = TrailNode( enter_a, Direction.WEST )

        # Then        
        outs = node.get_out_nodes()
        assert len(outs) == 2
        assert outs[0].tile in [enter_b, enter_c]
        assert outs[1].tile in [enter_b, enter_c]
        assert outs[0] <> outs[1]

        # And when
        node = node.get_out_nodes()[0]
        outs = node.get_out_nodes()

        # Then
        assert len(outs) == 1
        assert (node.tile is enter_b and outs[0].tile is tile_b) or \
               (node.tile is enter_c and outs[0].tile is tile_c)

    def test_eq( self ):
        tile1 = Tile( Vec3D, Tile.Type.FLAT )
        tile2 = Tile( Vec3D, Tile.Type.FLAT )

        assert TrailPosition( tile1, 200 ) == TrailPosition( tile1, 200 )
        assert not (TrailPosition( tile1, 200 ) <> TrailPosition( tile1, 200 ))
        assert TrailPosition( tile2, 200 ) <> TrailPosition( tile1, 200 )
        assert TrailPosition( tile1, 300 ) <> TrailPosition( tile1, 200 )

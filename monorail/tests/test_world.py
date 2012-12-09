
import os

from monorail.koon.geo import Vec3D
from monorail.tiles import Tile, Direction, Trail
from monorail.world import Level, Playfield
from monorail.player import *
from monorail.pickups import *


class TestLevel:

    def test_get_add_tile( self ):
        level = Level()

        assert level.get_tile( 0, 0 ) is None
        assert level.get_tile( -1, 9 ) is None

        tile1 = Tile( Vec3D(), Tile.Type.FLAT )
        tile2 = Tile( Vec3D(), Tile.Type.EAST_SLOPE_TOP )
        level.set_tile( tile1 )
        assert level.get_tile( 0, 0 ) is not None
        assert level.get_tile( 0, 0 ).type == Tile.Type.FLAT

        level.set_tile( tile2 )
        assert level.get_tile( 0, 0 ) is not None
        assert level.get_tile( 0, 0 ).type == Tile.Type.EAST_SLOPE_TOP

        level.remove_tile( 0, 0 )
        assert level.get_tile( 0, 0 ) is None


    def test_save_load_level( self ):
        level = Level()
        level_loaded = Level()

        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        level.set_tile( Tile( Vec3D(0,1,0), Tile.Type.SOUTH_SLOPE_TOP ) )
        assert level.get_tile(0,1).trail.type == Trail.Type.HILL
        level.set_tile( Tile( Vec3D(1,3,0), Tile.Type.SOUTH_SLOPE_BOT ) )
        assert level.get_tile(0,1).trail.type == Trail.Type.HILL
        level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.WEST_SLOPE_TOP ) )

        assert level.get_tile(0,0).get_neighbor( Direction.SOUTH ) is not None
        assert level.get_tile(0,0).get_neighbor( Direction.SOUTH ).type == Tile.Type.SOUTH_SLOPE_TOP

        level.save("saveloadtest.lvl");
        level_loaded.set_tile( Tile( Vec3D(2,2,0), Tile.Type.NORTH_SLOPE_TOP ) )
        level_loaded.load("saveloadtest.lvl");

        assert level_loaded.get_tile( 0, 0 ) is not None
        assert level_loaded.get_tile( 0, 0 ).type == Tile.Type.FLAT
        assert level_loaded.get_tile( 0, 1 ) is not None
        assert level_loaded.get_tile( 0, 1 ).type == Tile.Type.SOUTH_SLOPE_TOP
        assert level_loaded.get_tile( 1, 3 ) is not None
        assert level_loaded.get_tile( 1, 3 ).type == Tile.Type.SOUTH_SLOPE_BOT
        assert level_loaded.get_tile( 1, 0 ) is not None
        assert level_loaded.get_tile( 1, 0 ).type == Tile.Type.WEST_SLOPE_TOP
        assert level_loaded.get_tile( 1, 1 ) is None

        # check neighbors
        assert level_loaded.get_tile(0,0).get_neighbor( Direction.SOUTH ) is not None
        assert level_loaded.get_tile(0,0).get_neighbor( Direction.SOUTH ).type == Tile.Type.SOUTH_SLOPE_TOP

        os.remove("saveloadtest.lvl")


    def test_neighbors( self ):
        level = Level();

        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        level.set_tile( Tile( Vec3D(0,1,0), Tile.Type.FLAT ) )
        level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.WEST_SLOPE_TOP ) )
        level.set_tile( Tile( Vec3D(1,1,0), Tile.Type.WEST_SLOPE_BOT ) )

        neighbor = level.get_tile( 0,0 ).get_neighbor( Direction.SOUTH )
        assert neighbor is not None
        assert neighbor.type == Tile.Type.FLAT
        assert neighbor == level.get_tile(0,1)

        neighbor = level.get_tile( 0,1 ).get_neighbor( Direction.NORTH )
        assert neighbor == level.get_tile(0,0)

        neighbor = level.get_tile( 0,0 ).get_neighbor( Direction.EAST )
        assert neighbor is None

        neighbor = level.get_tile( 0,1 ).get_neighbor( Direction.EAST )
        assert neighbor == level.get_tile(1,1)

        level.remove_tile( 0, 1 )
        neighbor = level.get_tile( 0,0 ).get_neighbor( Direction.SOUTH )
        assert neighbor is None

    def test_slope_neighbors( self ):
        level = Level()

        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.SOUTH_SLOPE_TOP ) )
        level.set_tile( Tile( Vec3D(-1,2,0), Tile.Type.SOUTH_SLOPE_BOT ) )

        neighbor = level.get_tile( 0,0 ).get_neighbor( Direction.SOUTH )
        assert neighbor is not None and neighbor.type == Tile.Type.SOUTH_SLOPE_BOT

        neighbor = level.get_tile( -1,2 ).get_neighbor( Direction.NORTH )
        assert neighbor is not None and neighbor.type == Tile.Type.SOUTH_SLOPE_TOP

    def test_get_flat_tile( self ):
        level = Level()

        level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.WEST_SLOPE_TOP ) )
        level.set_tile( Tile( Vec3D(5,5,0), Tile.Type.FLAT ) )
        level.set_tile( Tile( Vec3D(1,1,0), Tile.Type.WEST_SLOPE_BOT ) )
        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )

        assert level.get_first_flat_tile() == level.get_tile(0,0) \
               or level.get_first_flat_tile() == level.get_tile(5,5)

        first_tile = False;
        second_tile = False;

        for i in range (0, 20): # chance is realy small that all 20 will be same
            t = level.get_random_flat_tile()
            if t == level.get_tile(5,5):
                first_tile = True
            elif t == level.get_tile(0,0):
                second_tile = True
            else:
                assert False

        assert first_tile and second_tile

class TestPlayfield:

    def test_goldcar_ranking( self ):
        """Given a playfield with 5 goldcars
        When all goldcars have different scores
        Then get_goldcar_ranking returns them ordered"""
        # Given
        playfield = Playfield()
        playfield.goldcars = [GoldCar(None, i) for i in range(0,5)]

        # When
        playfield.goldcars[0].score = 55
        playfield.goldcars[1].score = 12
        playfield.goldcars[2].score = 100
        playfield.goldcars[3].score = 0
        playfield.goldcars[4].score = 25

        # Then
        ranking = playfield.get_goldcar_ranking()

        assert len(ranking) == 5
        for goldcars in ranking:
            assert len(goldcars) == 1

        assert ranking[0][0] is playfield.goldcars[2]
        assert ranking[1][0] is playfield.goldcars[0]
        assert ranking[2][0] is playfield.goldcars[4]
        assert ranking[3][0] is playfield.goldcars[1]
        assert ranking[4][0] is playfield.goldcars[3]

    def test_goldcar_ranking( self ):
        """Given a playfield with 6 goldcars
        When some goldcars have same scores
        Then get_goldcar_ranking returns in same list"""
        # Given
        playfield = Playfield()
        playfield.goldcars = [GoldCar(None, i) for i in range(0,6)]

        # When
        playfield.goldcars[0].score = 0
        playfield.goldcars[1].score = 12
        playfield.goldcars[2].score = 100
        playfield.goldcars[3].score = 0
        playfield.goldcars[4].score = 100
        playfield.goldcars[5].score = 0

        # Then
        ranking = playfield.get_goldcar_ranking()

        assert len(ranking) == 3

        assert len(ranking[0]) == 2
        assert len(ranking[1]) == 1
        assert len(ranking[2]) == 3

        assert playfield.goldcars[0] in ranking[2]
        assert playfield.goldcars[1] in ranking[1]
        assert playfield.goldcars[2] in ranking[0]
        assert playfield.goldcars[3] in ranking[2]
        assert playfield.goldcars[4] in ranking[0]
        assert playfield.goldcars[5] in ranking[2]

    def test_is_free_position( self ):
        """Given a playfield with goldcar and some flat tiles
        When goldcar occupies a tile
        And we have a position on another tile close to goldcar
        Then is_free_position returns false
        """
        # Given
        playfield = Playfield()

        playfield.level = Level()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(2,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(3,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(4,0,0), Tile.Type.FLAT ) )

        # When
        playfield.goldcars = [
            GoldCar( TrailPosition(playfield.level.get_tile(2,0), 900), 1 )]

        pos = TrailPosition(playfield.level.get_tile(1,0), 100)

        # Then
        assert not playfield.is_free_position( pos )

    def test_isnt_free_position( self ):
        """Given a level with some flat tiles
        When a goldcar occupies a tile
        And we have a position on another tile far from goldcar
        Then is_free_position returns true
        """
        # Given
        playfield = Playfield()

        playfield.level = Level()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(2,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(3,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(4,0,0), Tile.Type.FLAT ) )

        # When
        playfield.goldcars = [
            GoldCar( TrailPosition(playfield.level.get_tile(2,0), 900), 1 )]

        pos = TrailPosition(playfield.level.get_tile(2,0), 100)

        # Then
        assert playfield.is_free_position( pos )


    def test_get_free_position( self ):
        """Given a playfield with some tiles and goldcar
        When get_free_position is called
        Then that position doesn't collide with goldcar
        """
        # Given
        playfield = Playfield()

        playfield.level = Level()

        playfield.level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(1,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(2,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(3,0,0), Tile.Type.FLAT ) )
        playfield.level.set_tile( Tile( Vec3D(4,0,0), Tile.Type.FLAT ) )

        playfield.goldcars = [
            GoldCar( TrailPosition(playfield.level.get_tile(1,0), 500), 1 )]

        for i in range(0, 256):
            # When
            pos = playfield.get_free_position()

            # Then
            if pos is not None:
                assert playfield.is_free_position( pos )


    def test_normal_portal_handling( self ):
        """Given a goldcar on a small track with 2 portals
           When goldcar rides through one portal
           Then it comes out of the other"""
        # Given
        level = Level()
        portalA = Enterance( Vec3D(2,0,0) )
        tileAA = Tile(       Vec3D(1,0,0), Tile.Type.FLAT )
        tileA = Tile(        Vec3D(0,0,0), Tile.Type.FLAT )
        tileB = Tile(        Vec3D(0,1,0), Tile.Type.FLAT )
        tileC = Tile(        Vec3D(0,2,0), Tile.Type.FLAT )
        tileCC = Tile(       Vec3D(1,2,0), Tile.Type.FLAT )
        portalC = Enterance( Vec3D(2,2,0) )

        level.set_tile( portalA )
        level.set_tile( tileAA )
        level.set_tile( tileA )
        level.set_tile( tileB )
        level.set_tile( tileC )
        level.set_tile( tileCC )
        level.set_tile( portalC)

        goldcar = GoldCar( TrailPosition( tileB, 0), 0 )
        #goldcar.pos.reverse_progress()

        playfield = Playfield()
        playfield.level = level
        playfield.goldcars = [goldcar]

        order = [tileB, tileC, tileCC, portalC, portalA, tileAA, tileA, tileB]
        order_at = 0

        count = 0
        while order_at < len(order)-1 and count < 1000:
            playfield.game_tick()

            print goldcar.pos.tile, goldcar.pos.progress

            if goldcar.pos.tile == order[ order_at ]:
                pass
            elif goldcar.pos.tile == order[ order_at+1 ]:
                order_at += 1
            else:
                assert False, "unknown tile after " + str(order_at)

            count += 1

        assert  count < 1000

    def test_edge_portal_handling( self ):
        """Given a goldcar on a small track with 2 portals
           When goldcar rides through one portal
           Then it comes out of the other"""
        # Given
        level = Level()
        portalA = Enterance( Vec3D(1,0,0) )
        tileA = Tile(        Vec3D(0,0,0), Tile.Type.FLAT )
        tileB = Tile(        Vec3D(0,1,0), Tile.Type.FLAT )
        tileC = Tile(        Vec3D(0,2,0), Tile.Type.FLAT )
        portalC = Enterance( Vec3D(1,2,0) )

        level.set_tile( portalA )
        level.set_tile( tileA )
        level.set_tile( tileB )
        level.set_tile( tileC )
        level.set_tile( portalC)

        goldcar = GoldCar( TrailPosition( tileB, 0), 0 )
        #goldcar.pos.reverse_progress()

        playfield = Playfield()
        playfield.level = level
        playfield.goldcars = [goldcar]

        order = [tileB, tileC, portalC, portalA, tileA, tileB]
        order_at = 0

        count = 0
        while order_at < len(order)-1 and count < 1000:
            playfield.game_tick()

            print goldcar.pos.tile, goldcar.pos.progress

            if goldcar.pos.tile == order[ order_at ]:
                pass
            elif goldcar.pos.tile == order[ order_at+1 ]:
                order_at += 1
            else:
                assert False, "unknown tile after " + str(order_at)

            count += 1

        assert  count < 1000



##
##    def test_pickup_count_remains_same_on_collision( self ):
##        """Given a playfield with 2 goldcars and one diamond
##           When the goldcars collide
##           Then the pickup count of diamond remains 1 the entire time"""
##        # Given
##        level = Level()
##
##        tileA = Tile( Vec3D(0,1,0), Tile.Type.FLAT )
##        tileB = Tile( Vec3D(0,3,0), Tile.Type.FLAT )
##
##        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
##        level.set_tile( tileA )
##        level.set_tile( Tile( Vec3D(0,2,0), Tile.Type.FLAT ) )
##        level.set_tile( tileB )
##        level.set_tile( Tile( Vec3D(0,4,0), Tile.Type.FLAT ) )
##
##        playfield = Playfield()
##        playfield.level = level
##
##        # FIRST A BEFORE B
##        goldcarA = GoldCar( TrailPosition( tileA, tileA.get_length()/2 ), 0 )
##        goldcarB = GoldCar( TrailPosition( tileB, tileB.get_length()/2 ), 1 )
##        goldcarB.pos.reverse_progress()
##
##        playfield.goldcars = [goldcarA, goldcarB]
##
##        # When
##        goldcarA.collectible = Diamond()
##
##        while goldcarB.collectible == None:
##            playfield.game_tick(None)
##
##            # Then
##            assert playfield.get_pickup_count( Diamond ) == 1
##
##        assert playfield.get_pickup_count( Diamond ) == 1
##
##        # THEN B BEFORE A
##        goldcarA = GoldCar( TrailPosition( tileA, tileA.get_length()/2 ), 0 )
##        goldcarB = GoldCar( TrailPosition( tileB, tileB.get_length()/2 ), 1 )
##        goldcarB.pos.reverse_progress()
##
##        playfield.goldcars = [goldcarA, goldcarB]
##
##        # When
##        goldcarB.collectible = Diamond()
##
##        while goldcarA.collectible == None:
##            playfield.game_tick(None)
##
##            # Then
##            assert playfield.get_pickup_count( Diamond ) == 1
##
##        assert playfield.get_pickup_count( Diamond ) == 1

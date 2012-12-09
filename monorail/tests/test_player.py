
from monorail.koon.geo import Vec3D
from monorail.tiles import *
from monorail.player import *
from monorail.world import Level, Playfield

def setup_module( module ):
    pygame.init()

def teardown_module( module ):
    pygame.quit()


class TestGoldCar:

    def test_constructor( self ):
        tile = Tile( Vec3D(), Tile.Type.FLAT )
        g = GoldCar( TrailPosition( tile, 0 ), 0 )


    def test_collision( self ):
        tile = Tile( Vec3D(), Tile.Type.FLAT, Trail.Type.NS )

        goldcar1 = GoldCar( TrailPosition( tile, 100 ), 0 )
        goldcar2 = GoldCar( TrailPosition( tile, 100 + GoldCar.COLLIDE_DISTANCE + 20 ), 0 )

        goldcar1.handle_collision( goldcar2 )
        assert goldcar1.pos == TrailPosition( tile, 100 )
        assert goldcar2.pos == TrailPosition( tile, 100 + GoldCar.COLLIDE_DISTANCE + 20 )

        goldcar1.speed = 15
        goldcar2.pos.reverse_progress()
        goldcar2.speed = 15

        goldcar1.game_tick()
        goldcar2.game_tick()

        goldcar1.handle_collision( goldcar2 )
        assert goldcar1.pos.get_distance( goldcar2.pos ) < GoldCar.COLLIDE_DISTANCE + 20
        assert goldcar1.pos.get_distance( goldcar2.pos ) >= GoldCar.COLLIDE_DISTANCE


        goldcar1 = GoldCar( TrailPosition( tile, 100 ), 0 )
        goldcar2 = GoldCar( TrailPosition( tile, 100 + GoldCar.COLLIDE_DISTANCE + 10 ), 0 )

        goldcar1.speed = 30
        goldcar2.speed = 10

        print goldcar1.pos.progress
        print goldcar2.pos.progress

        goldcar1.game_tick()
        goldcar2.game_tick()

        print goldcar1.pos.progress
        print goldcar2.pos.progress
        print GoldCar.COLLIDE_DISTANCE

        print goldcar1.speed
        print goldcar2.speed

        goldcar1.handle_collision( goldcar2 )
        assert goldcar1.pos.get_distance( goldcar2.pos ) < GoldCar.COLLIDE_DISTANCE + 20
        assert goldcar1.pos.get_distance( goldcar2.pos ) >= GoldCar.COLLIDE_DISTANCE


    def test_goldcar_rides_to_next_tile( self ):
        """Given a goldcar on one of 2 sequent tiles
           When the goldcar rides past the first one
           Then the goldcar is located on the second one"""
        # Given
        level = Level()
        tileA = Tile( Vec3D(0,0,0), Tile.Type.FLAT )
        tileB = Tile( Vec3D(0,1,0), Tile.Type.FLAT )
        level.set_tile( Tile( Vec3D(0,-1,0), Tile.Type.FLAT ) )
        level.set_tile( tileA )
        level.set_tile( tileB )
        level.set_tile( Tile( Vec3D(0,2,0), Tile.Type.FLAT ) )


        goldcar = GoldCar( TrailPosition( tileA, 0 ), 0 )


        count = 0
        while goldcar.pos.tile != tileB and count < 100:
            goldcar.game_tick()
            print goldcar.pos.tile, goldcar.pos.progress
            count += 1

        assert count < 100

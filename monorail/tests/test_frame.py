
from monorail.koon.gfx import Surface

from monorail.frame import *

def setup_module( module ):
    resman.read("data/resources.cfg")
    pygame.init()
    pygame.display.set_mode((800,600))

def teardown_module( module ):
    pygame.quit()


class TestFrame:
    def test_get_view_for_playfield( self ):
        """Given a playfield and a Frame
           When we request the view of the playfield
           Then we get a PlayfieldView object"""

        # Given
        frame = Frame( None, 0.0, 0 )
        # When
        views = frame.get_views( Playfield() )
        # Then
        assert isinstance( views[0], PlayfieldView )


    def test_draw_code( self ):
        # Given
        frame = Frame( Surface((800,600)), 20.1, 0.4 )

        tileA = Tile( Vec3D(0,1,0), Tile.Type.FLAT )
        tileB = Tile( Vec3D(0,3,0), Tile.Type.FLAT )

        level = Level()
        level.set_tile( Tile( Vec3D(0,0,0), Tile.Type.FLAT ) )
        level.set_tile( tileA )
        level.set_tile( Tile( Vec3D(0,2,0), Tile.Type.FLAT ) )
        level.set_tile( tileB )
        level.set_tile( Tile( Vec3D(0,4,0), Tile.Type.FLAT ) )

        playfield = Playfield()
        playfield.level = level

        goldcarA = GoldCar( TrailPosition( tileA, tileA.get_length()/2 ), 0 )
        goldcarB = GoldCar( TrailPosition( tileB, tileB.get_length()/2 ), 1 )
        goldcarB.pos.reverse_progress()

        playfield.goldcars = [goldcarA, goldcarB]

        # When
        frame.draw( Diamond() )
        frame.draw( Dynamite() )
        frame.draw( Torch() )
        frame.draw( Key() )
        #frame.draw( Mirror() )
        frame.draw( Oiler() )
        frame.draw( Multiplier() )
        frame.draw( Balloon() )
        frame.draw( Ghost() )
        frame.draw( CopperCoin() )
        frame.draw( GoldBlock() )
        frame.draw( RockBlock() )
        frame.draw( Lamp() )
        frame.draw( Axe() )
        frame.draw( Flag(goldcarA) )
        #frame.draw( Leprechaun() )

        frame.draw( tileA )

        frame.draw( Enterance( Vec3D(0,0,0) ) )
        #frame.draw( RailGate( Vec3D(0,0,0) ) )

        frame.draw( goldcarA )

        frame.draw( level )

        frame.draw( playfield )

        # Then all passes fine

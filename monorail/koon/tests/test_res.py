
import pygame
from monorail.koon.res import resman
import monorail.koon.geo as geo

class TestResourceManager:
    def test_get( self ):
        f = open( "resources.tmp", "w" )
        f.write("""
            place1 = Rectangle {
                x = 10
                y = 20
                width  = 100
                height = 50
            }
            pos = Vec2D {
                x = 10
                y = 20
            }
            loading = Loading...
            reloading = Reloading...
            timeout = 44
            en = Language {
                findit = Find it
            }
        """)
        f.close()

        resman.read( "resources.tmp" )

        assert resman.get("loading") == "Loading..."
        assert resman.get("reloading", str) == "Reloading..."
        assert resman.get("timeout", int) == 44

        assert resman.get("place1") == pygame.Rect( 10, 20, 100, 50 )

        assert resman.get("pos", int) == geo.Vec2D( 10, 20 )

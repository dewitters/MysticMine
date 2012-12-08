
import random

import koon.gfx as gfx
import koon.geo as geo
from koon.res import resman

from playerview import GoldCarView
import frame as frm
import tiles

class LevelView:

    def __init__( self, model ):
        self.model = model

        self.background = None

    def init_background( self ):
        self.background = gfx.Surface( (800,600) )
        frame = frm.Frame( self.background, 0, 0 )
        frame.X_OFFSET, frame.Y_OFFSET = 20, 300

        for tile in self.model.tiles:
            if not isinstance( tile, tiles.Enterance ):
                x = tile.pos.x * 32 + tile.pos.y * 32 + frame.X_OFFSET
                y = -tile.pos.x * 16 + tile.pos.y * 16 + frame.Y_OFFSET
                pos = geo.Vec2D( x, y )

                tile_surf = resman.get("game.tile%d_surf" % tile.type)
                tile_surf.nr = random.randint(0,4)
                tile_surf.draw( frame.surface, pos )

    def draw_background( self, frame ):
        for tile in self.model.tiles:
            if not isinstance( tile, tiles.Enterance ):
                x = tile.pos.x * 32 + tile.pos.y * 32 + frame.X_OFFSET
                y = -tile.pos.x * 16 + tile.pos.y * 16 + frame.Y_OFFSET
                pos = geo.Vec2D( x, y )

                tile_surf = resman.get("game.tile%d_surf" % tile.type)
                if not hasattr( tile, "view_surf_nr" ):
                    tile.view_surf_nr = random.randint(0,4)
                tile_surf.nr = tile.view_surf_nr
                tile_surf.draw( frame.surface, pos )

    def draw( self, frame ):
        if frame.optimize_speed:
            if self.background is None:
                self.init_background()

            self.background.draw( frame.surface, (0,0) )
        else:
            self.draw_background( frame )

        #for tile in self.model.tiles:
        #    frame.draw( tile )

    z = property( lambda self: -8000 )
    submodels = property( lambda self: self.model.tiles )


class PlayfieldView:

    def __init__( self, model ):
        self.model = model

        self.dark_surf = None

    def draw( self, frame ):
        frame.X_OFFSET, frame.Y_OFFSET = 20, 300

        draw_models = []
        draw_models.append( self.model.level )
        draw_models.extend( self.model.goldcars )
        frame.draw_z( draw_models )

        if self.model.explosion is not None:
            self.model.explosion.draw( frame )

        if self.dark_surf is None:
            self.dark_surf = gfx.Surface( frame.surface.get_size() )

        if self.model.dark_counter is not None:
            alpha = self.model.dark_counter
            if alpha > 255:
                alpha = 256 - (alpha%256)
            self.dark_surf.set_alpha( alpha )
            self.dark_surf.draw( frame.surface, (0, 0) )


import random

import pygame

from koon.geo import Vec2D
from koon.gfx import SpriteFilm, Font
from koon.res import resman

from tiles import *

class TileView:
    def __init__( self, model ):
        self.model = model
        self.sprite_nr = None
        if self.model.type == Tile.Type.FLAT:
            self.sprite_nr = random.randint(0,4)

    def get_pos( self, frame ):
        x = self.model.pos.x * 32 + self.model.pos.y * 32 + frame.X_OFFSET
        y = -self.model.pos.x * 16 + self.model.pos.y * 16 + frame.Y_OFFSET

        return Vec2D( x, y )

    def get_pickup_pos( self, frame ):
        x, y = self.model.get_center()
        return Vec2D( x, y )

    def draw( self, frame ):
        if self.model.type == Tile.Type.FLAT:
            pos = Vec2D( self.model.pos.x * 32 + self.model.pos.y * 32 + frame.X_OFFSET,
                        -self.model.pos.x * 16 + self.model.pos.y * 16 + frame.Y_OFFSET)

            if self.model.is_selected:
                selected_surf = resman.get("game.selected_tile_surf")
                selected_surf.draw( frame.surface, pos )

            trail_surf = resman.get("game.trail%d_surf" % self.model.trail.type)
            trail_surf.draw( frame.surface, pos )

        if self.model.pickup is not None:
            frame.draw( self.model.pickup )

    z = property( lambda self: -self.model.pos.x * 16 + self.model.pos.y * 16 - 28 )


class EnteranceView( TileView ):
    def __init__( self, model ):
        self.model = model

    def draw( self, frame ):
        pos = self.get_pos( frame )

        if self.model.is_north_exit():
            tile_surf = resman.get("game.exitbotnorth_surf")
            tile_surf.draw( frame.surface, pos )
        else:
            tile_surf = resman.get("game.exitboteast_surf")
            tile_surf.draw( frame.surface, pos )

    z = property( lambda self: -self.model.pos.x * 16 + self.model.pos.y * 16 - 16 )

class EnteranceTopView( TileView ):
    def __init__( self, model ):
        self.model = model

    def draw( self, frame ):
        pos = self.get_pos( frame )

        if self.model.is_north_exit():
            tile_surf = resman.get("game.exittopnorth_surf")
            tile_surf.draw( frame.surface, pos )
        else:
            tile_surf = resman.get("game.exittopeast_surf")
            tile_surf.draw( frame.surface, pos )

    z = property( lambda self: -self.model.pos.x * 16 + self.model.pos.y * 16 + 32 )


class RailGateView( TileView ):
    def __init__( self, model ):
        TileView.__init__( self, model )

        self.sprite = copy.copy(resman.get("game.railgate_sprite"))

##    def game_tick( self ):
##        Tile.game_tick( self )
##        #self.sprite.nr = (self.sprite.nr+1) % 12
##
##        if self.trail.type == Trail.Type.NS:
##            if self.sprite.nr > 5:
##                self.sprite.nr = 0
##            if self.is_down and self.sprite.nr <> 0:
##                self.sprite.nr -= 1
##            elif not self.is_down and self.sprite.nr <> 5:
##                self.sprite.nr += 1
##        elif self.trail.type == Trail.Type.EW:
##            if self.sprite.nr < 6:
##                self.sprite.nr = 6
##            if self.is_down and self.sprite.nr <> 6:
##                self.sprite.nr -= 1
##            elif not self.is_down and self.sprite.nr <> 11:
##                self.sprite.nr += 1

    def draw( self, frame ):
        TileView.draw( self, frame )

        pos = self.get_pos( frame )

        self.sprite.draw( frame.surface, pos )

    z = property( lambda self: -self.model.pos.x * 16 + self.model.pos.y * 16 )

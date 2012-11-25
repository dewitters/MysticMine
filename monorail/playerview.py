#!/usr/bin/env python

from koon.geo import Vec2D
from koon.res import resman
from koon.gfx import Timer, Font

from tiles import *
from pickups import Oiler, Ghost


class GoldCarView (object):
    
    def __init__( self, model ):
        self.model = model
        
        self.sprite = copy.copy(resman.get("game.car%d_sprite" % (model.nr+1)))
        
        self.motionblur = []
        self.motionblur_cnt = 0
        self.motionblur_timer = Timer( 25 )
        self.alpha_surfs = {}
        self.ghost_sprite = None

    def align_car_to_track( self, pos ):
        """Find the right car rotation/angle"""
        if pos is None: return

        if pos.tile.type == Tile.Type.FLAT:
            in_dir  = pos.tile.trail.get_in_direction()
            out_dir = pos.tile.trail.get_out_direction()

            if in_dir in [Direction.EAST, Direction.WEST]:
                in_sprite = 0;
            else:
                in_sprite = 6;

            if out_dir in [Direction.EAST, Direction.WEST]:
                out_sprite = 0;
            else:
                out_sprite = 6;
            
            # Turn reversed
            if( in_dir  == Direction.EAST and out_dir == Direction.SOUTH ): in_sprite = 12
            if( out_dir == Direction.EAST and in_dir  == Direction.SOUTH ): out_sprite = 12
            if( in_dir  == Direction.WEST and out_dir == Direction.NORTH ): in_sprite = 12
            if( out_dir == Direction.WEST and in_dir  == Direction.NORTH ): out_sprite = 12
            
            interpol = float(abs(pos.progress)) / float(pos.tile.get_length())
                            
            self.sprite.nr = int(in_sprite * (1.0 - interpol) + out_sprite * interpol) % 12

        elif pos.tile.type in [Tile.Type.NORTH_SLOPE_TOP, Tile.Type.NORTH_SLOPE_BOT]:
            self.sprite.nr = 16

        elif pos.tile.type in [Tile.Type.EAST_SLOPE_TOP, Tile.Type.EAST_SLOPE_BOT]:
            self.sprite.nr = 12

        elif pos.tile.type in [Tile.Type.SOUTH_SLOPE_TOP, Tile.Type.SOUTH_SLOPE_BOT]:
            self.sprite.nr = 19

        elif pos.tile.type in [Tile.Type.WEST_SLOPE_TOP, Tile.Type.WEST_SLOPE_BOT]:
            self.sprite.nr = 15

    def get_pos( self, frame ):
        return self.model.pos + (self.model.speed * frame.interpol)
        
    def get_pickup_pos( self, frame ):
        if self.model.pos is None: return None
        x, y = self.get_pos( frame ).get_screen_position()
        return Vec2D( x, y - 20 )

    def draw( self, frame ):
        if self.model.pos is None: return
        pos = self.get_pos( frame )

        self.align_car_to_track(pos)

        # show amount of gold in car
        self.sprite.nr += 20 * self.model.amount

        while self.motionblur_timer.do_tick( frame.time_sec ):
            self.motionblur_tick(pos)

        # draw motion blur
        if isinstance( self.model.modifier, Oiler ):
            diff = 1.0 / (len(self.motionblur)+1)
            alpha = 0.0 + diff*2
            for ghost in self.motionblur:
                if not self.alpha_surfs.has_key( alpha ):
                    self.alpha_surfs[alpha] = self.sprite.surface.get_blended( alpha )
                    
                ghost[1].surface = self.alpha_surfs[alpha]
                ghost[1].draw( frame.surface, Vec2D(ghost[0][0] + frame.X_OFFSET, ghost[0][1] + frame.Y_OFFSET) )
                alpha += diff

        screen_x, screen_y = pos.get_screen_position()
        screen_x += frame.X_OFFSET
        screen_y += frame.Y_OFFSET

        if isinstance( self.model.modifier, Ghost ):
            if self.ghost_sprite is None:
                self.ghost_sprite = copy.copy( self.sprite )
                self.ghost_sprite.surface = self.sprite.surface.get_blended( 0.6 )
            self.ghost_sprite.nr = self.sprite.nr
            self.ghost_sprite.draw( frame.surface, Vec2D(screen_x, screen_y) )
        else:
            self.sprite.draw( frame.surface, Vec2D(screen_x, screen_y) )

    def motionblur_tick( self, pos ):
        if isinstance( self.model.modifier, Oiler ):
            if self.motionblur_cnt == 0:
                self.motionblur.append( (pos.get_screen_position(), copy.copy(self.sprite)) )
            self.moctionblur_cnt = (self.motionblur_cnt+1) % 2
            while len( self.motionblur ) > 3:
                self.motionblur.pop(0)
        else:
            self.motionblur = []

    def get_z( self ):
        if self.model.pos is None:
            return -999
        else:
            return self.model.pos.get_screen_position()[1]
    z = property( get_z )

    def get_submodels( self ):
        result = []
        if self.model.collectible is not None:
            result.append( self.model.collectible )
        if self.model.modifier is not None:
            result.append( self.model.modifier )
        return result    
    submodels = property( get_submodels )
        

                

        

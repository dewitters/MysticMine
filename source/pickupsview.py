#!/usr/bin/env python

import random

import pygame

from koon.geo import Vec2D
import koon.geo as geo
from koon.gfx import SpriteFilm, Font, LoopAnimationTimer, PingPongTimer, Timer
from koon.res import resman
import pickups
import event
import tiles

class PickupView:
    def __init__( self ):
        self.pos = None
        self.jump_pos = None

    def get_z( self ):
        if self.pos is None:
            return -999
        else:
            return self.pos.y + 64
    z = property( get_z )
    
    def get_pos( self, frame ):
        self.pos = None
        if self.model.container is None or not hasattr( self.model.container, "views" ): return None

        self.pos = self.model.container.views[0].get_pickup_pos( frame )

        if self.model.jump_cnt is not None:
            if self.jump_pos is None:
                self.jump_pos = self.pos

            x = geo.lin_ipol( self.model.jump_cnt, self.jump_pos.x, self.pos.x )
            y = geo.lin_ipol( self.model.jump_cnt, self.jump_pos.y, self.pos.y )
            height = self.model.jump_cnt
            if self.model.jump_cnt > 0.5:
                height = 1.0 - self.model.jump_cnt
            self.pos = Vec2D( x, y - 30 * height)
        else:
            self.jump_pos = None

        return self.pos

class TorchView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model
        
        self.sprite = resman.get("game.torch_sprite").clone()
        
    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )

class KeyView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model
        
        self.sprite = resman.get("game.key_sprite")
        self.animTimer = LoopAnimationTimer( 25, 0, 19 )                
        
    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )

class MirrorView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.mirror_sprite").clone()
        self.animTimer = LoopAnimationTimer( 25, 0, 9 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 10) )

class OilerView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.oiler_sprite").clone()

    def draw( self, frame ):
        if self.get_pos( frame ) is not None and self.model.goldcar is None: # only draw on tile
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class MultiplierView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

    def draw( self, frame ):
        if self.get_pos( frame ) is None: return

        font = Font(size = 28, color = (255,0,0))
        pos = self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET)
        if self.model.goldcar is not None:
            pos += Vec2D(0, 20)
            
        font.draw("x2", frame.surface, pos.get_tuple(), Font.CENTER, Font.MIDDLE)

class BalloonView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model
        
        self.sprite = resman.get("game.balloon_sprite")
        
    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )
    
class GhostView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.ghost_sprite").clone()

    def draw( self, frame ):
        if self.get_pos( frame ) is not None and self.model.goldcar is None: # only draw on tile
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )

class CopperCoinView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.copper_sprite").clone()
        self.animTimer = LoopAnimationTimer( 25, 0, self.sprite.max_x )
        self.animTimer.set_frame( 0, random.randint(0,self.sprite.max_x-1) )

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class GoldBlockView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.gold_sprite").clone()
        self.animTimer = LoopAnimationTimer( 25, 0, 15 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class RockBlockView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.rock_sprite").clone()
        self.animTimer = LoopAnimationTimer( 25, 0, 15 )

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET + 10) )

class DiamondView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.diamond_sprite").clone()
        self.animTimer = LoopAnimationTimer( 25, 0, 4 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class DynamiteView (PickupView):
    class Sparkle:
        def __init__( self, pos ):
            self.pos = pos
            self.life = 10 + int(random.random() * 2)
            self.move = Vec2D( random.uniform( -2.5, 2.5 ), random.uniform( -2.5, 0.0 ) )
            self.surf = resman.get("game.sparkle_surf")
            width, height = self.surf.get_size()
            self.center = Vec2D( width/2, height/2 )

        def game_tick( self ):
            self.life -= 1
            self.pos += self.move
            self.move.y += 0.1

        def is_dead( self ):
            return self.life <= 0

        def draw( self, frame ):
            pos = self.pos + self.center + Vec2D( frame.X_OFFSET, frame.Y_OFFSET )
            self.surf.draw( frame.surface, pos )
        
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.dynamite_sprite").clone()
        self.sprite_delta = 1
        self.prev_life = 1.0
        w, h = self.sprite.get_size()
        self.sparkle_offset = Vec2D( 7, -h + 24 )
        self.sparkle_line = Vec2D( 0, -22 )

        self.sparkles = []
        self.sparkle_timer = Timer( 25 )

    def draw( self, frame ):
        if self.get_pos(frame) is None: return

        # no time... must implement... bad code...
        if self.model.life < pickups.Dynamite.DEC * 18 and\
           self.model.life != self.prev_life:
            self.prev_life = self.model.life
            
            self.sprite.nr += self.sprite_delta

            if self.sprite.nr < 0:
                self.sprite.nr = 0
                self.sprite_delta = 1
            elif self.sprite.nr >= 4:
                self.sprite.nr = 3
                self.sprite_delta = -1
                event.Event.dynamite_tick()
        
        while self.sparkle_timer.do_tick( frame.time_sec ):
            self.sparkle_tick( frame )
                    
        self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D( frame.X_OFFSET, frame.Y_OFFSET ) )
        for sparkle in self.sparkles:
            sparkle.draw( frame )

    def sparkle_tick( self, frame ):
        if self.model.life > pickups.Dynamite.DEC * 18:
            for i in range(3):
                pos = self.get_pos(frame) + self.sparkle_offset + self.sparkle_line * self.model.life
                self.sparkles.append( DynamiteView.Sparkle( pos ) )

        new_sparkles = []
        for sparkle in self.sparkles:
            sparkle.game_tick()
            if not sparkle.is_dead():
                new_sparkles.append( sparkle )
        self.sparkles = new_sparkles        

class LampView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.lamp_sprite").clone()
        #self.animTimer = LoopAnimationTimer( 25, 0, 4 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            #self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class AxeView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.axe_sprite").clone()
        # FIXME: make it pingpong instead of loop
        self.animTimer = PingPongTimer( 25, 0, 8 )

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

class FlagView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.flag%d_sprite" % (model.goldcar.nr+1))
        self.animTimer = LoopAnimationTimer( 20, 0, 8 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )

class LeprechaunView (PickupView):
    def __init__( self, model ):
        PickupView.__init__( self )
        self.model = model

        self.sprite = resman.get("game.leprechaun_sprite").clone()
        #self.animTimer = LoopAnimationTimer( 25, 0, 4 )        

    def draw( self, frame ):
        if self.get_pos( frame ) is not None:
            #self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.get_pos(frame) + Vec2D(frame.X_OFFSET, frame.Y_OFFSET - 20) )


#!/usr/bin/env python

import pygame
import random

import koon.snd as snd
from koon.geo import Vec2D
from koon.res import resman
import koon.gfx as gfx

from pickups import *
import pickups

class Point (object):
    def __init__( self, score, pos ):
        if score > 0:
            self.text = "+" + str(score)
        else:
            self.text = str(score)

        self.pos = pos
        self.life = 25

        self.font = gfx.Font( "data/edmunds.ttf", color=(255,255,255), size=16, use_antialias = True )

    def update( self ):
        self.life -= 1

    def draw( self, frame ):
        pos = (self.pos[0] + frame.X_OFFSET,
               self.pos[1] + frame.Y_OFFSET + self.life - 50)
        
        self.font.draw( self.text, frame.surface, pos,
                        align=gfx.Font.CENTER, valign=gfx.Font.MIDDLE )
        
    def is_alive( self ):
        return self.life >= 0

class Event (object):

    def __init__( self ):
        self.points = []
        self.play_fuse = False

    @staticmethod
    def update():
        new_points = []
        for point in Event.instance.points:
            point.update()
            if point.is_alive():
                new_points.append( point )
        Event.instance.points = new_points

        if Event.instance.play_fuse and \
           not resman.get("game.fuse_sound").is_playing():
            resman.get("game.fuse_sound").play(-1)
        elif not Event.instance.play_fuse and \
             resman.get("game.fuse_sound").is_playing():
            resman.get("game.fuse_sound").stop()
        Event.instance.play_fuse = False
        
    @staticmethod
    def dynamite_fuse():
        Event.instance.play_fuse = True

    @staticmethod
    def dynamite_tick():
        resman.get("game.dynamite_tick_sound").play()        

    @staticmethod
    def coin_pickup( score, carpos ):
        resman.get("game.coin_sound").play()        

        Event.instance.points.append( Point( score, carpos.get_screen_position() ) )
    
    @staticmethod
    def flag_pickup( score, carpos ):
        resman.get("game.collect_sound").play()

        Event.instance.points.append( Point( score, carpos.get_screen_position() ) )
    
    @staticmethod
    def carhit():
        resman.get("game.carhit_sound").play()

    @staticmethod
    def clock_ring():
        resman.get("game.clockring_sound").play()

    @staticmethod
    def clock():
        resman.get("game.clock_sound").play()

    @staticmethod
    def diamond():
        resman.get("game.diamond_sound").play()

    @staticmethod
    def collect( score, carpos ):
        resman.get("game.collect_sound").play()

        Event.instance.points.append( Point( score, carpos.get_screen_position() ) )

    @staticmethod
    def fireworks_start():
        resman.get("gui.fireworks0_sound").play()

    @staticmethod
    def fireworks_explode():
        resman.get("gui.fireworks%d_sound" % random.randint(1,3)).play()

    @staticmethod
    def explosion():
        resman.get("game.explosion_sound").play()

    @staticmethod
    def pickaxe():
        resman.get("game.pickaxe_sound").play()

    @staticmethod
    def pickaxe_pickup():
        resman.get("game.pickaxe_pickup_sound").play()

    @staticmethod
    def pickup():
        resman.get("game.pickup_sound").play()

    @staticmethod
    def lamp():
        resman.get("game.pickaxe_pickup_sound").play()

    @staticmethod
    def rock():
        resman.get("game.pickaxe_pickup_sound").play()

    @staticmethod
    def rock_drop():
        resman.get("game.rock_sound").play()

    @staticmethod
    def button():
        resman.get("gui.button_sound").play()

    @staticmethod
    def playerkey():
        resman.get("gui.button_sound").play()

    @staticmethod
    def sound_test():
        resman.get("game.coin_sound").play()

    @staticmethod
    def switch_trail():
        resman.get("game.railswitch_sound").play()

Event.instance = Event()


class Explosion:
    class GoldParticle:
        def __init__( self, start_pos, end_tile ):
            self.start_pos = start_pos
            self.end_tile = end_tile
            self.pos = start_pos
            self.progress = 0.0

        def game_tick( self ):
            if self.progress <= 1.0:
                end_pos = self.end_tile.get_center()
                end_pos = Vec2D( end_pos[0], end_pos[1] )

                speed = 20.0 / (end_pos - self.start_pos).length()
                self.progress += speed

                self.pos = self.start_pos * (1.0 - self.progress) + end_pos * self.progress

                if self.progress > 1.0 and self.end_tile.pickup is None:
                    self.end_tile.pickup = pickups.CopperCoin()
                    x, y = self.end_tile.get_center()
                    self.end_tile.pickup.container = self.end_tile

        def is_dead( self ):
            return self.progress > 1.0
        
        def render( self, surface, x_offset, y_offset ):
            if self.progress <= 1.0:
                pos = self.pos
                gold_sprite = resman.get("game.copper_sprite")
                gold_sprite.draw( surface, pos + Vec2D(x_offset, y_offset) )
                
    
    def __init__( self, pos, end_tiles ):
        self.particles = []
        for tile in end_tiles:
            self.particles.append( Explosion.GoldParticle( pos, tile ) )

        self.pos = pos

        self.sprite = resman.get("game.explosion_sprite").clone()
        self.animTimer = None

        Event.explosion()

        
    def game_tick( self ):
        for particle in self.particles:
            particle.game_tick()

            if particle.is_dead():
                self.particles.remove( particle )

    def draw( self, frame ):
        for particle in self.particles:
            particle.render( frame.surface, frame.X_OFFSET, frame.Y_OFFSET )

        if self.animTimer is None:
            self.animTimer = gfx.LoopAnimationTimer( 20, 0, 16 ) # real maxframe is in draw
            self.animTimer.set_frame( frame.time_sec, 0 )
                

        if self.sprite is not None:
            self.sprite.nr = self.animTimer.get_frame( frame.time_sec )
            self.sprite.draw( frame.surface, self.pos + Vec2D(frame.X_OFFSET, frame.Y_OFFSET) )

            if self.sprite.nr >= 15:
                self.sprite = None
        
    def is_alive( self ):
        return self.sprite is not None or len(self.particles > 0)

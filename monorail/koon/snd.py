#!/usr/bin/env python

import pygame
import pygame.mixer as mixer

def pre_init():
    mixer.pre_init(22050, -16, 2, 2048)

def init():
    mixer.init()
    pygame.mixer.set_num_channels(16)

def deinit():
    mixer.quit()


class Music (object):
    our_music_volume = 0.8
    our_current_music = None
    
    def __init__( self, filename = None ):
        self.sound = None
        self.channel = None
        if filename is not None:
            self.load( filename )

    def load( self, filename ):
        self.sound = mixer.Sound( filename )

    def play( self, loop = -1 ):
        self.sound.set_volume( Music.our_music_volume )
        self.channel = self.sound.play( loop )
        Music.our_current_music = self.sound
        
    def stop( self ):
        self.sound.stop()

    def fadeout( self, millisec ):
        self.sound.fadeout( millisec )

    def is_playing( self ):
        return self.channel is not None and self.channel.get_sound() is self.sound

    @staticmethod
    def set_global_volume( volume ):
        assert volume >= 0.0
        assert volume <= 1.0

        Music.our_music_volume = volume

        if Music.our_current_music is not None:
            Music.our_current_music.set_volume( volume )

    @staticmethod
    def get_global_volume():
        return Music.our_music_volume
    

class Sound (object):
    our_sound_volume = 0.8
    
    def __init__( self, filename = None ):
        self.sound = None
        self.channel = None
        if filename is not None:
            self.load( filename )

    def load( self, filename ):
        self.sound = mixer.Sound( filename )

    def play( self, loop = 0 ):
        """for infiniteloop, set loop to -1"""
        self.sound.set_volume( Sound.our_sound_volume )
        self.channel = self.sound.play( loop )
        
    def stop( self ):
        self.sound.stop()

    def fadeout( self, millisec ):
        self.sound.fadeout( millisec )

    def is_playing( self ):
        return self.channel is not None and self.channel.get_sound() is self.sound

    @staticmethod
    def set_global_volume( volume ):
        assert volume >= 0.0
        assert volume <= 1.0

        Sound.our_sound_volume = volume

    @staticmethod
    def get_global_volume():
        return Sound.our_sound_volume
    

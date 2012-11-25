#!/usr/bin/env python

import random

import koon.snd as snd
from koon.res import resman

class MusicManager (object):

    def __init__( self ):
        self.songs = [resman.get("game.game_music0"),
                      resman.get("game.game_music1")]
        
        self.music = None
        self.index = 0

    def play( self ):
        if self.music is None:
            self.music = self.songs[ self.next_index() ]
            
        self.music.play(-1)

    def stop( self ):
        if self.music is not None:
            self.music.fadeout( 1000 )
            self.music = None

    def play_other( self ):
        if self.music is not None:
            self.music.stop()
            
        self.music = self.songs[ self.next_index() ]

        self.music.play(-1)
    
    def game_tick( self ):
        if self.music is not None and not self.music.is_playing():
            self.play_other()

    def next_index( self ):
        self.index = (self.index + 1) % len(self.songs)
        return self.index
    
class SoundManager (object):

    @staticmethod
    def set_sound_volume( volume ):
        snd.Sound.set_global_volume( volume )

    @staticmethod
    def get_sound_volume():
        return snd.Sound.get_global_volume()

    @staticmethod
    def set_music_volume( volume ):
        snd.Music.set_global_volume( volume )

    @staticmethod
    def get_music_volume():
        return snd.Music.get_global_volume()
    

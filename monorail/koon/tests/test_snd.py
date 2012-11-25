#!/usr/bin/env python

import time

import pygame
import monorail.koon.snd as snd

def setup_module( module ):
    pygame.init()
    pygame.display.set_mode((800,600))

    snd.init()

def teardown_module( module ):
    pygame.quit()

    snd.deinit()
    

class TestMusic:

    def test_is_playing( self ):
        music = snd.Music("data/music/heartland.ogg")

        music.play()
        time.sleep(0.1)
        assert music.is_playing()

        music.stop()
        time.sleep(0.1)
        assert not music.is_playing()

class TestSound:

    def test_is_playing( self ):
        sound = snd.Sound("data/snd/coin.wav")

        sound.play()
        time.sleep(0.1)
        assert sound.is_playing()

        sound.stop()
        time.sleep(0.1)
        assert not sound.is_playing()


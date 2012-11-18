#!/usr/bin/env python

import os

import pygame

from source.koon.res import resman
import source.koon.gfx as gfx
import source.koon.geo as geo

import source.player as m_player
import source.playerview as m_playerview
import source.frame as m_frame

def setup_module( module ):
    resman.read("data/resources.cfg")
    pygame.init()
    pygame.display.set_mode((800,600))

def teardown_module( module ):
    pygame.quit()
    

class TestGoldCarView:

    def test_get_pickup_pos( self ):
        """Given a goldcar and view
        when goldcar pos is None
        then get_pickup_pos returns None"""
        # Given
        goldcar = m_player.GoldCar( None, 1 )
        goldcarview = m_playerview.GoldCarView( goldcar )
        
        surface = gfx.Surface((20,20))
        frame = m_frame.Frame( surface, 0.0, 0.0 )
        frame.interpol = 0.0

        # Then
        goldcarview.get_pickup_pos( frame )



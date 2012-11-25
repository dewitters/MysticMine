#!/usr/bin/env python

import os

import pygame

from monorail.koon.res import resman
import monorail.koon.gfx as gfx
import monorail.koon.geo as geo

import monorail.pickups as pickups
import monorail.pickupsview as pickupsview
import monorail.frame as m_frame

def setup_module( module ):
    resman.read("data/resources.cfg")
    pygame.init()
    pygame.display.set_mode((800,600))

def teardown_module( module ):
    pygame.quit()
    

class Container:
    class View:
        def get_pickup_pos( self, frame ):
            return geo.Vec2D(10,10)

    def __init__( self ):
        self.views = [Container.View()]

class TestDrawingViews:

    def test_drawing( self ):
        self.draw( pickups.Torch, pickupsview.TorchView)
        self.draw( pickups.Key, pickupsview.KeyView)
        self.draw( pickups.Oiler, pickupsview.OilerView)
        self.draw( pickups.Balloon, pickupsview.BalloonView)
        self.draw( pickups.Ghost, pickupsview.GhostView)
        self.draw( pickups.CopperCoin, pickupsview.CopperCoinView)
        self.draw( pickups.GoldBlock, pickupsview.GoldBlockView)
        self.draw( pickups.RockBlock, pickupsview.RockBlockView)
        self.draw( pickups.Diamond, pickupsview.DiamondView)
        self.draw( pickups.Dynamite, pickupsview.DynamiteView )
        self.draw( pickups.Lamp, pickupsview.LampView)
        self.draw( pickups.Axe, pickupsview.AxeView)
#        self.draw( pickups.Flag, pickupsview.FlagView)

    def draw( self, Model, ModelView ):
        model = Model()
        model_view = ModelView( model )
        model.container = Container()

        surf = gfx.Surface((50,50))
        for i in range(0,10):
            time_sec = i * 0.001
            frame = m_frame.Frame( surf, time_sec, 0.0 )

            model_view.draw( frame )
        



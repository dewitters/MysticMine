#!/usr/bin/env python

import os

from source.koon.res import resman

from source.pickups import *
from source.player import *
from source.tiles import *

class TestFlag:

    def test_dirs( self ):
        # Given
        tile = Tile( Vec3D(), Tile.Type.FLAT )
        goldcar = GoldCar( TrailPosition( tile, 0 ), 0 )
        flag = Flag(goldcar)
        
        # When
        

        # Then

class TestDynamite:

    def test_is_good( self ):
        dynamite = Dynamite()

        assert not dynamite.is_good()
        assert dynamite.is_bad()

class TestLamp:

    def test_is_good( self ):
        lamp = Lamp()

        assert lamp.is_good()
        assert not lamp.is_bad()


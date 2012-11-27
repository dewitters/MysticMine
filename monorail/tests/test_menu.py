#!/usr/bin/env python

from monorail.menu import *

def setup_module( module ):
    resman.read("data/resources.cfg")
    pygame.init()
    pygame.display.set_mode((800,600))

def teardown_module( module ):
    pygame.quit()


class TestScreenLevelSelect:

    pass
#    def test_init( self ):
#        levelSelect = ScreenLevelSelect( None )

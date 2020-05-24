
import pygame
from pygame.locals import *

from .koon import gfx
from .koon.geo import Vec2D

from . import control as ctrl



class EventView:

    def __init__( self, model ):
        self.model = model

    def draw( self, frame ):
        for point in self.model.points:
            point.draw( frame )

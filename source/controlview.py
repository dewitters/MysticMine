#!/usr/bin/env python

import pygame
from pygame.locals import *

import koon.gfx as gfx
from koon.geo import Vec2D

import control as ctrl

class GroundControlView:

    def __init__( self, model ):
        self.model = model

        self.generation = -1
        self.show_best_score = True

    def game_tick( self, indev ):
        return

        if indev.key.went_down( K_t ):
            self.generation -= 1
        if indev.key.went_down( K_y ):
            self.generation += 1
        if indev.key.went_down( K_g ):
            self.show_best_score = not self.show_best_score
    
    def draw( self, frame ):
        return
    
        i = 0
        for tree in self.model.prediction_trees:
            car = self.model.playfield.goldcars[i]

            if tree.root_node is not None:

                if i == 0:                
                    font = gfx.Font( None, 20, (255,0,0) )
                else:
                    font = gfx.Font( None, 20, (0,255,0) )

                for gen in range(self.generation, self.generation + 1):
                    for ai_node in tree.get_nodes_of_generation( gen ):
                        node = ai_node.smartnode
                        tile = node.trailnode.tile

                        x = tile.pos.x * 32 + tile.pos.y * 32 + frame.X_OFFSET + 32
                        y = -tile.pos.x * 16 + tile.pos.y * 16 + frame.Y_OFFSET + 16 + (i * 10 - 10)

                        if self.show_best_score:                                                    
                            score = ai_node.get_best_score()
                        else:
                            score = ai_node.get_score()
                            
##                        font.draw( "%02.2f" % score, frame.surface, (x,y),
##                                   gfx.Font.CENTER, gfx.Font.MIDDLE )
                        font.draw( str(score), frame.surface, (x,y),
                                   gfx.Font.CENTER, gfx.Font.MIDDLE )
            

            i += 1

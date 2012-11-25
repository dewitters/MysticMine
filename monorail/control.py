#!/usr/bin/env python

import random

from koon.input import Mouse
from tiles import *
from pickups import *
import ai
import world
from event import Event


class GroundControl:
    """The main control center that interacts with the model
    """

    def __init__( self, playfield ):
        self.playfield = playfield
        self.controllers = []
        self.prediction_trees = []

        self.contains_ai = False

    def game_tick( self, indev ):
        # for debugging
        if hasattr(self, "views"):
            self.views[0].game_tick( indev )
        
        # check each goldcar's keys
        for controller in self.controllers:
            controller.do_tick( indev )

        # check mouse switching
        if indev.mouse.went_down( Mouse.LEFT ):
            mouse_x, mouse_y = pygame.mouse.get_pos()

            X_OFFSET, Y_OFFSET = 20, 300

            tile_x = (-mouse_y + (mouse_x+32)/2 - X_OFFSET/2 + Y_OFFSET) / 32
            tile_y = (mouse_y + (mouse_x-32)/2 - X_OFFSET/2 - Y_OFFSET) / 32
            
            tile = self.playfield.level.get_tile( tile_x, tile_y )

            if tile is not None and tile.is_switch():
                i = 0
                had_it = False
                for goldcar in self.playfield.goldcars:
                    if tile is goldcar.switch:
                        if i == 0:
                            tile.switch_it(goldcar.switch_dir)
                            Event.switch_trail()
                            had_it = True
                        else:
                            pass # Only free and goldcar1 locked tiles can be switched!
                            had_it = True
                    i += 1

                if not had_it:
                    tile.switch_it()

        if self.contains_ai: 
            self._update_prediction_trees()

    def add_controllers( self, controllers ):
        """Add the controllers to this ground control

        controllers - a list of controllers (in sequence with playfield goldcars)
        """
        i = 0
        for controller in controllers:
            controller.set_goldcar( self.playfield.goldcars[i] )
            controller.set_ground_control( self )
            self.controllers.append( controller )

            prediction_tree = ai.PredictionTree(256*2, 256/4)
            self.prediction_trees.append( prediction_tree )

            controller.prediction_tree = prediction_tree

            if not isinstance( controller, HumanController ):
                self.contains_ai = True
            
            i += 1

    def _update_prediction_trees( self ):
        i = 0
        for prediction_tree in self.prediction_trees:
            car = self.playfield.goldcars[i]

            if car.pos is not None:
                car_node = ai.AiNode_create( GoldcarNodeState(car), TrailNode(car.pos.tile, car.pos.get_in_direction()) )
                car_node.set_playfield( self.playfield )
                car_node.set_other_trees( self._get_other_prediction_trees(car) )

                if prediction_tree.root_node is None:
                    prediction_tree.set_root( ai.Node(car_node) )
                elif prediction_tree.root_node.smartnode.nequals(car_node):
                    prediction_tree.set_root( ai.Node(car_node) )
                prediction_tree.root_node.smartnode.set_playfield( self.playfield )
                prediction_tree.root_node.smartnode.carstate = GoldcarNodeState(car)

            prediction_tree.update()
##            if prediction_tree.root_node is not None:
##                print prediction_tree.root_node._best_score,
            i += 1
            
    def _get_other_prediction_trees( self, car ):
        """Return all prediction trees that are not from car.
        """
        trees = []
        i = 0
        for prediction_tree in self.prediction_trees:
            car_it = self.playfield.goldcars[i]

            if car_it is not car:
                trees.append( prediction_tree )

            i += 1        

        return trees

    def get_tree( self, car ):
        i = 0
        for prediction_tree in self.prediction_trees:
            car_it = self.playfield.goldcars[i]

            if car_it is car:
                return prediction_tree
            i += 1

        return None        
        
class Controller:    
    """Controller of a goldcar

    public members:
    - prediction_tree: the prediction tree of the goldcar
    """
    
    def __init__( self, goldcar ):
        """goldcar can be None"""
        self.goldcar = goldcar
        self.prediction_tree = None

    def set_goldcar( self, goldcar ):
        self.goldcar = goldcar

    def do_tick( self, indev ):
        pass

    def set_ground_control( self, ground_control ):
        self.ground_control = ground_control


class HumanController( Controller ):
    def __init__( self, goldcar, action_button ):
        """goldcar can be None"""
        Controller.__init__( self, goldcar )
        self.action_button = action_button

    def do_tick( self, indev ):
        if self.action_button.dev.went_down( self.action_button.button ):
            self.goldcar.keydown()

class GoldcarNodeState:
    def __init__( self, goldcar ):
        self.goldcar = goldcar
        self.collectible = goldcar.collectible
        self.modifier = goldcar.modifier


class AiController( Controller ):
    def __init__( self, goldcar, iq = 1.0 ):
        """goldcar can be None"""
        Controller.__init__( self, goldcar )
        self.prev_switch = None
        self.best_dir = None
        self.iq = iq
        
    def do_tick( self, indev ):
        if self.goldcar.switch is not None:
            switch_node = self.find_switch_node()
                        
            # find best direction for switch
            if switch_node is not None:
                best_childs = switch_node.get_best_childs()
                if best_childs is not None and len(best_childs) == 1:
                    self.best_dir = best_childs[0].smartnode.trailnode.in_dir.get_opposite()
                else:
                    self.best_dir = None
            else:
                self.best_dir = None
            
            self.handle_switching()

    # TODO: improve algorithm here!
    def find_switch_node( self ):
        node_it = self.prediction_tree.root_node
        while node_it is not None and \
              node_it.smartnode.nequals(ai.AiNode_create( None, TrailNode(self.goldcar.switch, self.goldcar.switch_dir) ) ):
            childeren = node_it.get_childeren()
            if childeren is not None and len( childeren ) > 0:
                best_childs = node_it.get_best_childs()
                if len(best_childs) > 0:
                    node_it = best_childs[0]
##                    if node_it._best_score < 0:
##                        print node_it._best_score                    
                else:
                    node_it = None
            else:
                node_it = None

        return node_it

    def handle_switching( self ):
        if random.random() < self.iq: # Smart move
            if self.best_dir is None:
                if random.randint(0,16) == 0:
                    self.goldcar.keydown()
            elif self.best_dir not in [self.goldcar.switch.trail.get_out_direction(), \
                                self.goldcar.switch.trail.get_in_direction()]:
                if random.random() < self.iq:
                    self.goldcar.keydown()
        else: # Stupid move
            if random.randint(0,32) == 0:
                self.goldcar.keydown()
            

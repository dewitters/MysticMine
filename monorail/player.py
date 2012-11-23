#!/usr/bin/env python

import copy

from pickups import *
from tiles import *
#from mysticmine import App
import world
from event import Event

class GoldCar:
    """A Car of Gold!

    Public members:
    - pos: TrailPosition
    - speed: the current speed
    - switch: next switch tile
    - switch_dist: distance to switch
    - score
    - amount: amount of gold in car (0,1,2,3)
    - collectible: current collectible on car    
    """
    COLLIDE_DISTANCE = 500

    def __init__( self, position, nr ):
        self.pos = position
        self.speed = 70
        self.switch = None
        self.switch_dir = Direction.NORTH
        self.score = 0
        self.collectible = None
        self.modifier = None
        self.nr = nr
        self.amount = 0

        self._key_went_down = 0
        
    def game_tick( self ):
        if self.pos is None: return
        old_tile = self.pos.tile

        MIN_SPEED = 140
        MAX_SPEED = 230
        SLOPE_ACCEL = 1.2
        SLOPE_SLOWDOWN = 0.8
        SPEEDUP = 1.05
        if isinstance( self.modifier, Oiler ):
            MIN_SPEED = 150
            SLOPE_SLOWDOWN = 0.15
            SPEEDUP = 1.5
        
        # slow down speed
        self.speed = int(self.speed * 0.99);
        
        # DESIGN: don't stop the car
        if self.pos.tile.type == Tile.Type.FLAT and self.speed < MIN_SPEED:
            self.speed = int((self.speed+5) * SPEEDUP )
        
        # when going down/up
        if (self.pos.is_reversed() and not isinstance(self.collectible, Balloon)) or \
                   (not self.pos.is_reversed() and isinstance(self.collectible, Balloon)):
            self.speed = min( [int(self.speed + SLOPE_ACCEL * self.pos.tile.get_angle()), MAX_SPEED] )
        else:
            self.speed = min( [int(self.speed - SLOPE_SLOWDOWN * self.pos.tile.get_angle()), MAX_SPEED] )
        
        if self.speed < 0:
            self.speed *= -1
            self.pos.reverse_progress()
            self.select_next_switch()

        # special case when ghost
        if isinstance( self.modifier, Ghost ):
            self.speed = (MIN_SPEED + MAX_SPEED) / 2
        
        # update position
        self.pos += self.speed
        
        # tile with goldcar on can't be switched
        if self.pos.tile <> old_tile:
            old_tile.trail.may_switch = True
            self.pos.tile.trail.may_switch = False
            self.select_next_switch()

        # Update collectible
        if self.collectible is not None:
            self.collectible.game_tick()

            if isinstance( self.collectible, Lamp ):
                self.score += self.collectible.score()

            # Powerup worked out?            
            if isinstance(self.collectible, PowerUp) \
               and self.collectible.is_done():
                self.collectible = None

        # Steal points from mirror
        if isinstance( self.modifier, Mirror ):
            self.score += self.modifier.twin.score
            self.modifier.twin.score = 0

        # Update modifier
        if self.modifier is not None:
            self.modifier.game_tick()
            # Powerup worked out?
            if self.modifier.is_done():
                
                if isinstance( self.modifier, Ghost ):
                    # playfield handles Ghost modifier
                    pass
                else:
                    self.modifier = None
        
        if self._key_went_down > 0:
            self._key_went_down -= 1

        # handle leprechaun
        if isinstance( self.collectible, Leprechaun ):
            if old_tile <> self.pos.tile and \
               self.score > 0 and \
               old_tile.pickup is None and \
               random.randint(0, 5) == 0:
                self.score -= 1
                old_tile.pickup = CopperCoin()

        # handle gate
        if isinstance( self.pos.tile, RailGate ) and \
           self.pos.tile.is_down and \
           self.pos.get_distance( TrailPosition(self.pos.tile, self.pos.tile.get_length()/2 )) < GoldCar.COLLIDE_DISTANCE/2:
            
            self.speed *= -1                                       

    def clear_switch_and_pos( self ):
        if self.switch is not None:
            self.switch.set_selected( False )
            self.switch = None
            self.pos.tile.trail.may_switch = True

    def select_next_switch( self ):
        if self.switch is not None:
            self.switch.set_selected( False )

        it = copy.copy( self.pos )
        #if it.get_tile().is_hill() and it.speed < 0:
        #   it.speed = -it.speed
        out_dir = it.get_out_direction()
        it.to_next_tile()
        self.switch_dist = it.tile.get_length()

        count = 0
        while not it.tile.is_switch() and count < 100:
            #if it.get_tile().is_hill() and it.tile.get_out_direction() == it.in_dir:
            #	self.switch_pos = None
            #	return            
            out_dir = it.get_out_direction()
            old_tile = it.tile
            it.to_next_tile()

            if old_tile == it.tile:
                # end of trail when same tile is returned as next
                self.switch = None
                return
            
            self.switch_dist += it.tile.get_length()

            count += 1

        if count < 100:
            self.switch = it.tile
            self.switch_dir = out_dir.get_opposite()
            self.switch.set_selected( True )
        else:
            self.switch = None

    def align_switch( self ):
        if self.switch is not None:
            self.switch.trail.align( self.switch_dir )

    def key_went_down( self ):
        return self._key_went_down > 0

    def keydown( self ):
        if self.switch is not None:
            self.switch.switch_it( self.switch_dir )
            Event.switch_trail()

        self._key_went_down = 2

        if isinstance( self.modifier, Mirror ):
            self.modifier.twin.keydown()

    def add_pickup( self, pickup ):
        multiplier = 1
        if isinstance( self.collectible, Multiplier ):
            multiplier = 2
        
        if isinstance( pickup, CopperCoin ):
            self.score += 1 * multiplier
            Event.coin_pickup( 1, self.pos )
        elif isinstance( pickup, GoldBlock ):
            self.score += 1 * multiplier
            Event.pickaxe()
        elif isinstance( pickup, Flag ):
            self.score += 1 * multiplier
            Event.flag_pickup( 1, self.pos )
        elif isinstance( pickup, Collectible ) or isinstance( pickup, PowerUp ):
            self.collectible = pickup
            self.collectible.goldcar = self
            self.collectible.container = self
            if isinstance( pickup, Diamond ):
                Event.diamond()
            elif isinstance( pickup, Axe ):
                Event.pickaxe_pickup()
            elif isinstance( pickup, RockBlock ):
                Event.rock()
            elif isinstance( pickup, Lamp ):
                Event.lamp()
            else:
                Event.pickup()
        elif isinstance( pickup, Modifier ):
            self.modifier = pickup
            self.modifier.set_goldcar( self )
            self.modifier.container = self
            Event.pickup()

    def switch_collectibles( self, car, other ):
        if car.collectible is not None:
            car.collectible.jump()
        if other.collectible is not None:
            other.collectible.jump()
        car.collectible, other.collectible = other.collectible, car.collectible
        if car.collectible is not None:
            car.collectible.container = car
        if other.collectible is not None:
            other.collectible.container = other


    def handle_collision( self, other ):
        if isinstance( self.modifier, Ghost ):
            if isinstance( self.modifier, Ghost ):
                if self.pos.get_distance( other.pos ) < GoldCar.COLLIDE_DISTANCE and \
                           self.collectible is None:
                    self.switch_collectibles( self, other )
                    
        elif isinstance( other.modifier, Ghost ):
            pass            
        else:
            SPEEDUP  = 1.05
            SLOWDOWN = 0.95

            # Handle collision
            if self.pos.get_distance( other.pos ) < GoldCar.COLLIDE_DISTANCE:
                Event.carhit()
                
                self.speed, other.speed = other.speed, self.speed
                if not self.pos.same_direction( other.pos ):
                    self.pos.reverse_progress()
                    other.pos.reverse_progress()                
                diff = GoldCar.COLLIDE_DISTANCE - self.pos.get_distance( other.pos )

                proportion1 = float(self.speed) / (self.speed + other.speed)
                proportion2 = float(other.speed) / (self.speed + other.speed)

                if not self.pos.same_direction( other.pos ):
                    self.pos += int(diff * proportion1)
                    other.pos += int(diff * proportion2)
                    self.speed *= SPEEDUP
                    other.speed *= SPEEDUP
                elif self.speed <= other.speed:
                    self.pos -= int(diff * proportion1)
                    other.pos += int(diff * proportion2) + 1 # for rounding
                    self.speed *= SLOWDOWN
                    other.speed *= SPEEDUP
                else:
                    self.pos += int(diff * proportion1) + 1 # for rounding
                    other.pos -= int(diff * proportion2)
                    self.speed *= SPEEDUP
                    other.speed *= SLOWDOWN

                self.switch_collectibles( self, other )

            # Handle too close (in real extreme cases!)
            elif self.pos.get_distance( other.pos ) < GoldCar.COLLIDE_DISTANCE * 3 / 2 \
                 and self.pos.same_direction( other.pos ) \
                 and abs( self.speed - other.speed ) < 10:
                if self.pos + self.pos.get_distance( other.pos ) == other.pos:
                    self.speed *= SLOWDOWN
                    other.speed *= SPEEDUP
                elif other.pos + self.pos.get_distance( other.pos ) == self.pos:
                    self.speed *= SPEEDUP
                    other.speed *= SLOWDOWN
                else:
                    assert False, "Should be one or the other!"

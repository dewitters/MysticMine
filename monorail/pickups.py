#!/usr/bin/env python

import random

from koon.geo import Vec2D
from koon.res import resman

from event import Event


class Pickup (object):
    """Object that cars can pick up.

    container: the object that owns this pickup
    """
    def __init__( self ):
        self._is_good = True

        self.container = None
        self.jump_cnt = None
    
    def game_tick( self ):
        if self.jump_cnt is not None:
            self.jump_cnt += 0.25
            if self.jump_cnt >= 1.0:
                self.jump_cnt = None

    def is_good( self ):
        return self._is_good

    def is_bad( self ):
        return not self._is_good

    def jump( self ):
        self.jump_cnt = 0.0

class Torch( Pickup ):
    pass

class PowerUp( Pickup ):
    """Gets passed along"""
    def __init__( self, time_to_live ):
        Pickup.__init__( self )
        self.goldcar = None
        self.time_to_live = time_to_live

    def game_tick( self ):
        Pickup.game_tick( self )
        if self.goldcar is not None:
            self.time_to_live -= 1
    
    def set_goldcar( self, goldcar ):
        self.goldcar = goldcar

    def is_done( self ):
        return self.time_to_live <= 0    

class Modifier( Pickup ):
    """Doesn't get passed along"""
    def __init__( self, time_to_live ):
        Pickup.__init__( self )
        self.goldcar = None
        self.time_to_live = time_to_live

    def game_tick( self ):
        Pickup.game_tick( self )
        if self.goldcar is not None:
            self.time_to_live -= 1
    
    def set_goldcar( self, goldcar ):
        self.goldcar = goldcar

    def is_done( self ):
        return self.time_to_live <= 0    

class Key( PowerUp ):
    def __init__( self ):
        PowerUp.__init__( self, 15*25 )

class Mirror( Modifier ):
    def __init__( self ):
        Modifier.__init__( self, 15*25 )
        self.twin = None

    def set_twin( self, twin ):
        self.twin = twin

    def get_twin( self, twin ):
        return self.twin

class Oiler( Modifier ):
    def __init__( self ):
        Modifier.__init__( self, 20*25 )

class Multiplier( PowerUp ):
    def __init__( self ):
        PowerUp.__init__( self, 15*25 )

class Balloon( PowerUp ):
    def __init__( self ):
        PowerUp.__init__( self, 20*25 )

class Ghost( Modifier ):
    def __init__( self ):
        Modifier.__init__( self, 15*25 )

class Dynamite( PowerUp ):
    DEC = 0.0015
    
    def __init__( self ):
        PowerUp.__init__( self, 0 )
        self.life = 1.0

        self._is_good = False

    def game_tick( self ):
        PowerUp.game_tick( self )
        if self.life > 0.0:
            self.life -= Dynamite.DEC        
        else:
            self.is_exploding = True

        if self.life > Dynamite.DEC * 18:
            Event.dynamite_fuse()
            
    def explode( self ):
        return self.life <= 0.0

    def is_done( self ):
        return False
            

class Collectible( Pickup ):
    """Goldcar can contain this pickup"""
    def __init__( self, is_good = True ):
        Pickup.__init__( self )
        self._is_good = is_good

class CopperCoin( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, True )

class GoldBlock( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, True )

class RockBlock( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, False )
        self.pos = Vec2D( 0, 0 )

class Diamond( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, True )

class Lamp( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, True )
        self.score_tick = 0

    def game_tick( self ):
        Collectible.game_tick( self )
        self.score_tick = (self.score_tick + 1) % 25

    def score( self ):
        if self.score_tick == 0:
            return 1
        else:
            return 0

class Axe( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, True )

class Flag( Collectible ):
    def __init__( self, goldcar ):        
        Collectible.__init__( self, True )
        self.goldcar = goldcar

class Leprechaun( Collectible ):
    def __init__( self ):
        Collectible.__init__( self, False )

class Bonus( Pickup ):
    pass

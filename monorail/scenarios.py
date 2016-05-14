
import random
from cPickle import *
import os
import gettext

from koon.geo import *

import pickups
from world import Playfield, Level
from event import Explosion
from tiles import *

## Handling localization, used for when running main
##current_lang = 'ru_RU'
#current_lang = 'en_US'
#
#import gettext
#gettext.install("monorail", "./data/locale" )
#lang = gettext.translation('monorail', "./data/locale", languages=[current_lang])
#
#lang.install()
#gettext.lang = lang
## End localisation


TIMEOUT = 60

TICKS_PER_SECOND = 25

class Scenario:
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        if timeout is not None:
            self.timeout = timeout * TICKS_PER_SECOND
        else:
            self.timeout = None
        self.goal = goal

        self.completed_time = 0

        self.pickups = pickups
        self.is_multiplayer = is_multiplayer

        self.ontime = True # if time is static/const, not adapted by skill

        self.restart()

    def restart( self ):
        pass

    def get_timeout( self ):
        """returns the current timeout, or None if no timeout"""
        if self.timeout is not None:
            return self.timeout / TICKS_PER_SECOND
        else:
            return None

    def game_tick( self ):
        self.handle_explosions()

        if self.timeout is not None:
            self.timeout -= 1
        self.completed_time += 1

        # Spawn pickups
        if self.pickups is not None and len( self.pickups ) > 0:
            sum_pickups = 0
            for pickup_class in self.pickups:
                sum_pickups += self.playfield.get_pickup_count( pickup_class )

            if sum_pickups < 1 and random.randint(0,TICKS_PER_SECOND*10) == 0:
                i = random.randint( 0, len(self.pickups)-1 )
                self.playfield.spawn_pickup( self.pickups[i]() )

        self.update_goldcar_amounts()

    def update_goldcar_amounts( self ):
        if len(self.playfield.goldcars) == 1 or not self.is_multiplayer:
            for goldcar in self.playfield.goldcars:
                if self.goal is not None and self.goal <> 0:
                    goldcar.amount = max([0, min([3, goldcar.score * 4 / self.goal])])
        else:
            ranking = self.playfield.get_goldcar_ranking()

            if len(ranking) > 1:
                inc = 3 / min([3, len(ranking)-1])
            else:
                inc = 3

            amount = min([3, ranking[0][0].score])
            prev_score = ranking[0][0].score
            for goldcars in ranking:
                amount -= min(inc, prev_score - goldcars[0].score)

                for goldcar in goldcars:
                    goldcar.amount = max([0, amount])

                prev_score = goldcars[0].score

    def is_finished( self ):
        if self.timeout is not None and self.timeout <= 0:
            return True

        if self.goal is not None:
            if self.is_multiplayer:
                for gc in self.playfield.goldcars:
                    if gc.score >= self.goal:
                        return True
            elif self.timeout is None or not self.ontime:
                return self.playfield.goldcars[0].score >= self.goal

        return False

    def has_won( self ):
        if not self.is_multiplayer:
            if self.goal is not None:
                return self.playfield.goldcars[0].score >= self.goal
            else:
                return True
        else:
            return self.playfield.goldcars[0] in self.playfield.get_goldcar_ranking()[0]

    def handle_explosions( self ):
        for goldcar in self.playfield.goldcars:
            if isinstance( goldcar.collectible, pickups.Dynamite ):
                if goldcar.collectible.explode():
                    old_score = goldcar.score
                    goldcar.score /= 2
                    x, y = goldcar.pos.get_screen_position()
                    end_tiles = [self.playfield.level.get_random_flat_tile() for i in range(0, old_score - goldcar.score) ]
                    self.playfield.explosion = Explosion( Vec2D( x, y ), end_tiles )
                    goldcar.collectible = None

    def _get_mission_txt( self ):
        return _("Your mission is...")
    mission_txt = property( _get_mission_txt )


class ScenarioCoinCollect( Scenario ):
    def __init__( self, timeout, goal, max_spawn, pickups, is_multiplayer = True, ontime = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )
        self.max_gold = max_spawn

        self.title = _("Coin Collect")
        self.ontime = ontime
        self.coin_start_cnt = goal

    def game_tick( self ):
        if self.playfield.get_pickup_count( pickups.CopperCoin ) < self.max_gold:
            self.playfield.spawn_pickup(pickups.CopperCoin())

        Scenario.game_tick( self )

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d coin", "%d coins", self.goal) % self.goal
            return _("Collect %(point)s in %(second)s.") % \
                   {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most coins in %d second.",\
                "Collect the most coins in %d second.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d coin.",\
                "Be the first to collect %d coins.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d coin.",\
                "Collect %d coins.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Collect the most coins")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Collect %d more coin",\
                        "Collect %d more coins",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d coin collected, ",\
                        "All %d coins collected, ",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Collect many coins")
    mission_txt = property( _get_mission_txt )


class ScenarioHoldLamp( Scenario ):
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Hold the Lamp")

    def restart( self ):
        self.nolamp = True

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d point", "%d points", self.goal) % self.goal
            return _("Gain %(point)s in %(second)s") % {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return _("Hold the lamp as long as possible.")
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to hold the lamp for %d second.",\
                "Be the first to hold the lamp for %d seconds.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Hold the lamp for %d second.",\
                "Hold the lamp for %d seconds.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        if self.nolamp:
            self.playfield.spawn_pickup(pickups.Lamp())
            self.nolamp = False

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Hold the lamp as long as possible")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Hold the lamp %d more second",\
                        "Hold the lamp %d more seconds",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "Goal achieved, %d bonus point",\
                        "Goal achieved, %d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Hold the lamp as long as possible")
    mission_txt = property( _get_mission_txt )


class ScenarioCutter( Scenario ):
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Gold Cutting")

    def restart( self ):
        self.noaxe = True

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d gold block", "%d gold blocks", self.goal) % \
                          self.goal
            return _("Cut %(goldblock)s in %(second)s") % \
                   {"goldblock":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most gold in %d second.",\
                "Collect the most gold in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d gold block.",\
                "Be the first to collect %d gold blocks.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d gold block.",\
                "Collect %d gold blocks.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        if self.noaxe:
            self.playfield.spawn_pickup(pickups.Axe())
            self.noaxe = False

        if self.playfield.get_pickup_count( pickups.GoldBlock ) < 1:
            self.playfield.spawn_pickup( pickups.GoldBlock() )

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Cut the most goldblocks")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Cut %d more gold block",\
                        "Cut %d more gold blocsk",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d gold block collected,",\
                        "All %d gold blocks collected,",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Cut as many gold blocks as possible")
    mission_txt = property( _get_mission_txt )

class ScenarioBlowup( Scenario ):
    START_SCORE = 0

    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Pass the Dynamite")

    def restart( self ):
        self.add_points = True
        self.explosion_timeout = 0

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d time", "%d times", self.goal) % self.goal
            return _("Avoid the dynamite %(times)s in %(second)s") % \
                   {"times":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Pass the Dynamite in %d second.",\
                "Pass the Dynamite in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None:
            return _("Do some stuff %d.") % self.goal
        else:
            assert False
    description = property(_get_description)


    def game_tick( self ):
        if self.add_points:
            for goldcar in self.playfield.goldcars:
                goldcar.score = ScenarioBlowup.START_SCORE
            self.add_points = False

        if self.explosion_timeout <= 0:
            if self.playfield.get_pickup_count( pickups.Dynamite ) < 1:
                cars = self.playfield.goldcars
                self.playfield.spawn_dynamite_on_car(cars[random.randint(0, len(cars)-1)])
        else:
            self.explosion_timeout -= 1

        Scenario.game_tick( self )

    def handle_explosions( self ):
        for goldcar in self.playfield.goldcars:
            if isinstance( goldcar.collectible, pickups.Dynamite ):
                if goldcar.collectible.explode():
                    old_score = goldcar.score
                    for c in self.playfield.goldcars:
                        c.score += 1
                    goldcar.score -= 1
                    #end_tiles = [self.playfield.level.get_random_flat_tile() for i in range(0, old_score - goldcar.score) ]
                    x, y = goldcar.pos.get_screen_position()
                    self.playfield.explosion = Explosion( Vec2D( x, y ) , [] )
                    self.explosion_timeout = 25 * 2
                    goldcar.collectible = None

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Avoid the dynamite")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Avoid the dynamite %d time.",\
                        "Avoid the dynamite %d times.",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d dynamite avoided,",\
                        "All %d dynamites avoided,",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Avoid the dynamite")
    mission_txt = property( _get_mission_txt )

class ScenarioRace( Scenario ):
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Race")

    def restart( self ):
        # contains the tiles where the flags are
        self.tiles = [None for i in range(0, 10)]

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d flag", "%d flags", self.goal) % self.goal
            return _("Collect %(point)s in %(second)s.") % \
                    {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most flags in %d second.",\
                "Collect the most flags in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d flag.",\
                "Be the first to collect %d flags.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d flag.",\
                "Collect %d flags.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        i = 0
        for gc in self.playfield.goldcars:
            while self.tiles[i] is None:
                self.tiles[i] = self.playfield.spawn_pickup( pickups.Flag(gc) )

            # Reset when flag is gone
            if self.tiles[i].pickup is None:
                self.tiles[i] = None

            i += 1

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Race to your flag")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Collect %d more flag",\
                        "Collect %d more flags",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d flag collected,",\
                        "All %d flags collected,",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Collect as many flags as possible")
    mission_txt = property( _get_mission_txt )

class ScenarioCollectRocks( Scenario ):
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Drop the rocks")

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d coin", "%d coins", self.goal) % self.goal
            return _("Collect %(point)s in %(second)s.") % \
                    {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most coins in %d second.",\
                "Collect the most coins in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d coin.",\
                "Be the first to collect %d coins.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d coin.",\
                "Collect %d coins.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        if self.playfield.get_pickup_count( pickups.CopperCoin ) < 20:
            self.playfield.spawn_pickup( pickups.CopperCoin() )

        if self.playfield.get_pickup_count( pickups.RockBlock ) < 3:
            self.playfield.spawn_pickup( pickups.RockBlock() )

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Collect the most points")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Collect %d more point",\
                        "Collect %d more points",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d point collected,",\
                        "All %d points collected,",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Collect as many points as possible")
    mission_txt = property( _get_mission_txt )

class ScenarioDiamondCollect( Scenario ):
    def __init__( self, timeout, goal, max_diamonds, pickups, is_multiplayer = True ):
        goalTen = goal
        if goalTen is not None:
            goalTen *= 10 # *10 because diamonds are worth 10
        Scenario.__init__( self, timeout, goalTen, pickups, is_multiplayer )
        self.max_diamonds = max_diamonds

        self.title = _("Diamond Collect")

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d diamond", "%d diamonds", self.goal/10) % (self.goal/10)
            return _("Collect %(point)s in %(second)s.") % \
                    {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most diamonds in %d second.",\
                "Collect the most diamonds in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d diamond.",\
                "Be the first to collect %d diamonds.",\
                self.goal/10) % (self.goal/10)
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d diamond.",\
                "Collect %d diamonds.",\
                self.goal/10) % (self.goal/10)
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        diamond_cnt = self.playfield.get_pickup_count( pickups.Diamond )

        if diamond_cnt < self.max_diamonds:
            self.playfield.spawn_pickup( pickups.Diamond() )

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Collect the most diamonds")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Collect %d more diamond",\
                        "Collect %d more diamonds",\
                        (self.goal - goldcar_score) / 10) % ((self.goal - goldcar_score) / 10)
                else:
                    return gettext.lang.ungettext(\
                        "All %d diamond collected,",\
                        "All %d diamonds collected,",\
                        self.goal / 10) % (self.goal / 10)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Collect as many diamonds as possible")
    mission_txt = property( _get_mission_txt )

class ScenarioCollectAll( Scenario ):
    def __init__( self, timeout, goal, pickups, is_multiplayer = True ):
        Scenario.__init__( self, timeout, goal, pickups, is_multiplayer )

        self.title = _("Collect Frenzy")

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            seconds_string = gettext.lang.ungettext("%d second", "%d seconds", seconds) % seconds
            goal_string = gettext.lang.ungettext("%d point", "%d points", self.goal) % self.goal
            return _("Collect %(point)s in %(second)s.") % \
                    {"point":goal_string, "second":seconds_string}
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most points in %d second.",\
                "Collect the most points in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Be the first to collect %d point.",\
                "Be the first to collect %d points.",\
                self.goal) % self.goal
        elif self.goal is not None and not self.is_multiplayer:
            return gettext.lang.ungettext(\
                "Collect %d point.",\
                "Collect %d points.",\
                self.goal) % self.goal
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        if self.playfield.get_pickup_count( pickups.CopperCoin ) < 15:
            self.playfield.spawn_pickup( pickups.CopperCoin() )
        if self.playfield.get_pickup_count( pickups.Diamond ) < 3:
            self.playfield.spawn_pickup( pickups.Diamond() )

        Scenario.game_tick( self )

    def _get_mission_txt( self ):
        if self.is_multiplayer:
            return _("Collect the most points")
        else:
            if self.goal is not None:
                goldcar_score = self.playfield.goldcars[0].score
                if goldcar_score < self.goal:
                    return gettext.lang.ungettext(\
                        "Collect %d more point",\
                        "Collect %d more points",\
                        self.goal - goldcar_score) % (self.goal - goldcar_score)
                else:
                    return gettext.lang.ungettext(\
                        "All %d point collected,",\
                        "All %d points collected,",\
                        self.goal) % (self.goal)\
                        + \
                        gettext.lang.ungettext(\
                        "%d bonus point",\
                        "%d bonus points",\
                        goldcar_score - self.goal) % (goldcar_score - self.goal)
            else:
                return _("Collect as many points as possible")
    mission_txt = property( _get_mission_txt )

class ScenarioPacman( Scenario ):
    def __init__( self, timeout, goal ):
        Scenario.__init__( self, timeout, goal, [], False ) # never pickups!

        self.title = _("Goldrush")
        self.ontime = False

    def restart( self ):
        self.is_init = False
        self.all_taken = False
        self.coin_start_cnt = 0

    def _get_description( self ):
        if self.timeout is not None:
            seconds = self.timeout / TICKS_PER_SECOND

        if self.timeout is not None and self.goal is not None:
            return gettext.lang.ungettext(\
                "Collect all coins in %d second.",\
                "Collect all coins in %d seconds.",\
                seconds) % seconds
        elif self.timeout is not None:
            return gettext.lang.ungettext(\
                "Collect the most coins in %d second.",\
                "Collect the most coins in %d seconds.",\
                seconds) % seconds
        elif self.goal is not None and self.is_multiplayer:
            return _("Collect the most coins.")
        elif self.goal is not None and not self.is_multiplayer:
            return _("Collect all coins.")
        else:
            assert False
    description = property(_get_description)

    def game_tick( self ):
        if not self.is_init:
            for tile in self.playfield.level.tiles:
                if tile.type == Tile.Type.FLAT:
                    tile.pickup = pickups.CopperCoin()
                    tile.pickup.container = tile
                    self.coin_start_cnt += 1
            self.is_init = True
            self.goal = self.coin_start_cnt
        else:
            if self.playfield.get_pickup_count( pickups.CopperCoin ) <= 0:
                self.all_taken = True

        Scenario.game_tick( self )

    def is_finished( self ):
        if self.timeout is not None:
            return self.timeout <= 0 or self.all_taken
        else:
            return self.all_taken

    def has_won( self ):
        return self.all_taken

    def _get_mission_txt( self ):
        return _("Collect all the coins")
    mission_txt = property( _get_mission_txt )

class Quest:
    """A sequence of scenarios with levels."""

    def __init__( self ):
        """Return an emtpy Quest."""
        self.scenarios = []
        self.level_nrs = []
        self.opponent_iqs_list = []
        self.progress = 0

    def add_level( self, scenario, level_nr, opponent_iqs = [] ):
        """Appends a new level with specific scenario and level"""
        assert isinstance(opponent_iqs, list)
        self.scenarios.append( scenario )
        self.level_nrs.append( level_nr )
        self.opponent_iqs_list.append( opponent_iqs )

    def create_scenario( self, skill = 1 ):
        """Create a new current scenario. It also creates the playfield"""
        scenario = copy.copy( self.scenarios[ self.progress ] )
        scenario.restart()
        playfield = Playfield()
        playfield.load( Level.get_filename( self.get_current_level_nr() ) )
        scenario.playfield = playfield

        if not scenario.ontime:
            if scenario.timeout is not None:
                scenario.timeout = int(scenario.timeout / skill)
        elif isinstance( scenario, ScenarioDiamondCollect ):
            if scenario.goal is not None:
                scenario.goal = int(scenario.goal * skill / 10) * 10
        else:
            if scenario.goal is not None:
                scenario.goal = int(scenario.goal * skill)

        return scenario

    def save_score( self, scenario ):
        stats = QuestStatistics()

        if not scenario.ontime:
            stats.add( self.progress, -scenario.completed_time )
        elif isinstance( scenario, ScenarioDiamondCollect ):
            stats.add( self.progress, scenario.playfield.goldcars[0].score / 10 )
        else:
            stats.add( self.progress, scenario.playfield.goldcars[0].score )


    def get_skill( self, scenario ):
        """Return the skill when you completed the level with that scenario's score."""

        if not scenario.ontime:
            if self.get_scenario().timeout is not None:
                if scenario.has_won():
                    return float(self.get_scenario().timeout) / scenario.completed_time
                else:
                    score = scenario.playfield.goldcars[0].score
                    estim_time = (float(scenario.completed_time) / score) * scenario.coin_start_cnt
                    return float(self.get_scenario().timeout) / estim_time
            else:
                return None
        else:
            if self.get_scenario().goal is not None:
                return float(scenario.playfield.goldcars[0].score) / self.get_scenario().goal
            elif len(scenario.playfield.goldcars) > 1:
                best_score = 1
                for car in scenario.playfield.goldcars[1:]:
                    best_score = max([best_score, car.score])
                return float(scenario.playfield.goldcars[0].score) / best_score
            else:
                return None

    def get_scenario( self ):
        return self.scenarios[ self.progress ]

    def get_current_level_nr( self ):
        """Return the current level
        """
        return self.level_nrs[ self.progress ]

    def get_opponent_iqs( self ):
        """Return the number of opponents
        """
        return self.opponent_iqs_list[ self.progress ]

    def to_next_level( self ):
        """Sets the next level as current"""
        if self.progress < len( self.scenarios ) - 1:
            self.progress += 1

    def to_level( self, level_nr ):
        self.progress = level_nr

    def get_level_count( self ):
        return len( self.scenarios )

class RandomQuest( Quest ):
    """A Random sequence of scenarios with levels"""
    MIN_LEVEL = 3
    MAX_LEVEL = 181

    def __init__( self, max_opponent_nr = 0 ):
        """Return an instance of RandomQuest"""

        # Fill available with everything
        self.available_pickups = []
        self.available_scenarios = [ScenarioCoinCollect]

        self.pickups = []
        self.scenarios = []
        self.to_next_level()
        self.max_opponent_nr = max_opponent_nr

    def create_scenario( self, goal_mult = 1 ):
        """Create a new current scenario. It also creates the playfield"""
        scenario = copy.copy( self.scenario )
        scenario.restart()
        playfield = Playfield()
        playfield.load( Level.get_filename( self.get_current_level_nr() ) )
        scenario.playfield = playfield
        return scenario

    def set_available_items( self, pickups, scenarios ):
        self.available_pickups = pickups
        self.available_scenarios = scenarios

        # reload pickups and scenarios
        self.pickups = []
        self.scenarios = []

    def get_current_level_nr( self ):
        return self.level_nr

    # TODO: replace with one that also deletes the item in sequence
    def _get_random_item( self, items ):
        return items[randint(0, len(items)-1)]

    def _get_random_pickup( self ):
        if len( self.pickups ) < 1:
            self._fill_pickups()

        return self._get_random_item( self.pickups )

    def _get_random_scenario( self ):
        if len( self.scenarios ) < 1:
            self._fill_scenarios()

        return self._get_random_item( self.scenarios )

    def _fill_pickups( self ):
        self.pickups.append([])
        for pickup in self.available_pickups:
            self.pickups.append([pickup])

    def _fill_scenarios( self ):
        TIMEOUT = 120 # 120

        if ScenarioCoinCollect in self.available_scenarios:
            self.scenarios.append(ScenarioCoinCollect( TIMEOUT, None, 1, self._get_random_pickup() ))
            self.scenarios.append(ScenarioCoinCollect( TIMEOUT, None, random.randint(3, 15), self._get_random_pickup() ))
        if ScenarioDiamondCollect in self.available_scenarios:
            self.scenarios.append(ScenarioDiamondCollect( TIMEOUT, None, 1, self._get_random_pickup() ))
        if ScenarioCollectRocks in self.available_scenarios:
            self.scenarios.append(ScenarioCollectRocks( TIMEOUT, None, self._get_random_pickup() ))
        if ScenarioCollectAll in self.available_scenarios:
            self.scenarios.append(ScenarioCollectAll( TIMEOUT, None, self._get_random_pickup() ))
        if ScenarioHoldLamp in self.available_scenarios:
            self.scenarios.append(ScenarioHoldLamp( TIMEOUT, None, self._get_random_pickup() ))
        if ScenarioBlowup in self.available_scenarios:
            self.scenarios.append(ScenarioBlowup( TIMEOUT, None, self._get_random_pickup() ))
        if ScenarioRace in self.available_scenarios:
            self.scenarios.append(ScenarioRace( TIMEOUT, None, self._get_random_pickup() ))
        if ScenarioCutter in self.available_scenarios:
            self.scenarios.append(ScenarioCutter( TIMEOUT, None, self._get_random_pickup() ))

    def to_next_level( self ):
        self.level_nr = random.randint( RandomQuest.MIN_LEVEL, RandomQuest.MAX_LEVEL )
        self.scenario = self._get_random_scenario()

    def get_opponent_iqs( self ):
        if self.max_opponent_nr < 1:
            return []
        else:
            #nr = random.randint(1, self.max_opponent_nr)
            nr = self.max_opponent_nr
            return [1.0 for i in range(0, nr)]

class SkillSet:
    """Contains the current and future set of skills that the players know"""
    ENTERANCE_EXIT, TRACK_SWITCH, GATE_SWITCH, UPDOWN, PASS_PICKUPS, \
    COIN_COLLECT, DIAMOND_COLLECT, ROCK_COLLECT, COLLECT_ALL, \
    HOLD_LAMP, CUTTER, BLOWUP, RACE, \
    OILER, DYNAMITE, BALLOON, KEY, GHOST, TORCH = range(19)

class QuestStatistics:

    def __init__( self, filename = "quest.stat"):
        self.filename = filename
        self.stats = {}
        self._load()

    def get( self, i ):
        if self.stats.has_key(i):
#            print i, self.stats[i]
            return max(self.stats[i])
        else:
            return None

    def add( self, i, score ):
        if self.stats.has_key(i):
            self.stats[i].append(score)
        else:
            self.stats[i] = [score]
        self._save()

    # FIXME: disable in release version!
    def _save( self ):
        pass
        #stats_file = open( self.filename, "wb" )

        #pickler = Pickler( stats_file, 2 )
        #pickler.dump( self.stats )

        #stats_file.close()

    def _load( self ):
        if os.path.exists(self.filename):
            stats_file = open( self.filename, "rb" )

            unpickler = Unpickler( stats_file )
            self.stats = unpickler.load()

            stats_file.close()


class QuestManager:
    """Singleton that manages all available quests"""

    MAIN_QUEST, SINGLE_RANDOM_QUEST, MULTI_RANDOM_QUEST = range( 3 )

    _singleton = None

    def __init__( self ):
        """Don't use this, but use get_instance() instead!"""

    @staticmethod
    def get_instance():
        """Return the singleton instance. Creates it on first call."""
        if QuestManager._singleton is None:
            QuestManager._singleton = QuestManager()
        return QuestManager._singleton

    def add( self, quest, scenario_class, level_nr, ai_count = 0, \
             pickups = [], xtra = None, ontime = True ):
        timeout = 120
        stats = QuestStatistics()
        goal = stats.get( quest.get_level_count() )

        ai = [0.5 for i in range(0,ai_count)]
        compete = False #ai_count > 0

        if compete:
            goal = None

        if scenario_class is ScenarioPacman:
            if goal is not None: goal = -goal / TICKS_PER_SECOND
            quest.add_level( ScenarioPacman( goal, 0 ), level_nr ) # goal here is really timeout
        elif scenario_class is ScenarioCoinCollect:
            if xtra is None: xtra = 1
            if not ontime:
                if goal is not None:
                    goal = -goal / TICKS_PER_SECOND
                count = 10 * xtra
                if xtra == 3: count = 20
                quest.add_level( ScenarioCoinCollect( goal, count, xtra, pickups, compete, False ),\
                                 level_nr, ai )
            else:
                quest.add_level( ScenarioCoinCollect( timeout, goal, xtra, pickups, compete ),\
                                 level_nr, ai )
        elif scenario_class is ScenarioBlowup:
            quest.add_level( ScenarioBlowup( timeout, goal, pickups, compete ), level_nr, ai )
        elif scenario_class is ScenarioDiamondCollect:
            if xtra is None: xtra = 1
            quest.add_level( ScenarioDiamondCollect( timeout, goal, xtra, pickups, compete ), level_nr, ai )
        elif scenario_class is ScenarioCollectAll:
            quest.add_level( ScenarioCollectAll( timeout, goal, pickups, compete ), level_nr, ai )
        elif scenario_class is ScenarioHoldLamp:
            quest.add_level( ScenarioHoldLamp( timeout, goal, pickups, compete ), level_nr, ai )
        elif scenario_class is ScenarioCutter:
            quest.add_level( ScenarioCutter( timeout, goal, pickups, compete ), level_nr , ai )
        elif scenario_class is ScenarioRace:
            quest.add_level( ScenarioRace( timeout, goal, pickups, compete ), level_nr,  ai )
        elif scenario_class is ScenarioCollectRocks:
            quest.add_level( ScenarioCollectRocks( timeout, goal, pickups, compete ), level_nr, ai )
        else:
            assert False, "Scenario not recognized!"

    def get_quest( self, quest_id ):
        if quest_id == QuestManager.MAIN_QUEST:
            quest = Quest()
            TIMEOUT = 120 # 120

            # -T-U-T-O-R-I-A-L-
            #
            #     add_level( SCENARIOXXXXXX(         TIMEOUT, GOAL, MAX, [PICKUPS],          COMPETE ), LEVEL, [A.I] ) #
##            quest.add_level( ScenarioCoinCollect(    None,    10,   1,   [],                 False   ), 0,     []    ) # Learn coins and switch
##            quest.add_level( ScenarioCoinCollect(    None,    20,   3,   [],                 False   ), 1,     []    ) # Learn larger playfield
##            quest.add_level( ScenarioCoinCollect(    None,    20,   3,   [],                 False   ), 2,     []    ) # Learn slopes
##            quest.add_level( ScenarioCoinCollect(    None,    15,   1,   [],                 False   ), 64,    []    ) # Learn slope loops
##            quest.add_level( ScenarioCoinCollect(    None,    20,   3,   [],                 False   ), 39,    [0.2] ) # Learn opponent
            self.add( quest, ScenarioCoinCollect, 0,  0, [], None, False ) # Learn coins and switch
            self.add( quest, ScenarioCoinCollect, 1,  0, [], 3, False ) # Learn larger playfield
            self.add( quest, ScenarioCoinCollect, 2,  0, [], 3, False ) # Learn slopes
            # Diamond
            self.add( quest, ScenarioDiamondCollect, 9, 0, [] )

            self.add( quest, ScenarioCoinCollect, 4, 1, [], 3 ) # Learn opponent
            self.add( quest, ScenarioDiamondCollect, 3, 0, [] ) # Learn slope loops with diamonds

            self.add( quest, ScenarioDiamondCollect, 10, 1, [] )

            self.add( quest, ScenarioPacman, 5, 0, [] ) # Learn packman
            #-----------------------------------------------------------------------------------------left-bottom-hill-#


            # -E-A-S-Y-
            #
            """
   pickups: pickups.Dynamite
            pickups.Balloon
            pickups.Oiler
            pickups.Torch
            pickups.Ghost
            pickups.Key
            """
            #     add_level( SCENARIOXXXXXX(         TIMEOUT, GOAL, MAX, [PICKUPS],          COMPETE ), LEVEL, [A.I] ) #
            # Dynamite
            self.add( quest, ScenarioBlowup, 6, 1, [] )
            self.add( quest, ScenarioDiamondCollect, 8, 2, [] )
            self.add( quest, ScenarioCoinCollect, 7, 1, [pickups.Dynamite], 2 )
            self.add( quest, ScenarioPacman, 11, 0, [] )
            self.add( quest, ScenarioCollectAll, 12, 0, [] )
            self.add( quest, ScenarioCollectAll, 13, 1, [] )
            self.add( quest, ScenarioBlowup, 14, 1, [] )
            self.add( quest, ScenarioCoinCollect, 15, 0, [] )
            self.add( quest, ScenarioDiamondCollect, 16, 0, [] )# complex level
            self.add( quest, ScenarioCoinCollect, 17, 1, [], 5 )
            self.add( quest, ScenarioPacman, 18, 0, [] )
            self.add( quest, ScenarioDiamondCollect, 19, 1, [] )
            self.add( quest, ScenarioCollectAll, 20, 0, [] )
            self.add( quest, ScenarioPacman, 21, 0, [] )
            #-----------------------------------------------------------------------------------------left-middle-hill-#
            ### Lamp
            self.add( quest, ScenarioHoldLamp, 22, 1, [] )
            self.add( quest, ScenarioCoinCollect, 23, 1, [], 1 )
            self.add( quest, ScenarioBlowup, 24, 2, [] )
            self.add( quest, ScenarioHoldLamp, 25, 1, [] )
            self.add( quest, ScenarioCollectAll, 26, 2, [] )
            self.add( quest, ScenarioDiamondCollect, 27, 1, [] )
            self.add( quest, ScenarioCoinCollect, 28, 1, [pickups.Dynamite], 3 )
            self.add( quest, ScenarioHoldLamp, 29, 2, [] )
            self.add( quest, ScenarioDiamondCollect, 30, 2, [] )
            self.add( quest, ScenarioPacman, 31, 0, [] )
            self.add( quest, ScenarioHoldLamp, 32, 2, [] )
            #---------------------------------------------------------------------------------------------left-top-hill-#
            ### Balloon
            self.add( quest, ScenarioCoinCollect, 33, 0, [pickups.Balloon], 3 )
            self.add( quest, ScenarioDiamondCollect, 34, 1, [] )
            self.add( quest, ScenarioHoldLamp, 35, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCollectAll, 36, 2, [] )
            self.add( quest, ScenarioCoinCollect, 37, 1, [pickups.Balloon], 1 )
            self.add( quest, ScenarioBlowup, 38, 1, [pickups.Balloon] )
            self.add( quest, ScenarioPacman, 39, 0, [] )
            self.add( quest, ScenarioCollectAll, 40, 0, [] )
            self.add( quest, ScenarioCoinCollect, 41, 1, [pickups.Balloon], 5 )
            self.add( quest, ScenarioHoldLamp, 42, 1, [] )
            self.add( quest, ScenarioCoinCollect, 43, 2, [pickups.Dynamite], 1 )
            #---------------------------------------------------------------------------------------centerleft-top-hill-#
            self.add( quest, ScenarioPacman, 44, 0, [] )


            # -M-E-D-I-U-M-
            #
            # (13), (16), 150, 152, 170
            ### Goldcutter Axe
            self.add( quest, ScenarioCutter, 45, 1, [] )
            self.add( quest, ScenarioCoinCollect, 46, 0, [pickups.Balloon], 5 )
            self.add( quest, ScenarioCutter, 47, 1, [] )
            self.add( quest, ScenarioHoldLamp, 48, 2, [pickups.Balloon] )
            self.add( quest, ScenarioBlowup, 49, 2, [] )
            self.add( quest, ScenarioDiamondCollect, 50, 0, [] )
            self.add( quest, ScenarioCutter, 51, 2, [pickups.Balloon] ) # FUN FUN FUN
            self.add( quest, ScenarioPacman, 52, 0, [] )
            #-----------------------------------------------------------------------------------centerleft-middle-hill-#
            self.add( quest, ScenarioHoldLamp, 53, 2, [] )
            self.add( quest, ScenarioCollectAll, 54, 0, [] )
            self.add( quest, ScenarioCutter, 55, 2, [] )
            self.add( quest, ScenarioDiamondCollect, 56, 2, [pickups.Balloon] )
            self.add( quest, ScenarioPacman, 57, 0, [] )
            ### Flags
            self.add( quest, ScenarioRace, 58, 1, [] )
            #-----------------------------------------------------------------------------------centerleft-bottom-hill-#
            self.add( quest, ScenarioHoldLamp, 59, 1, [] )
            self.add( quest, ScenarioDiamondCollect, 60, 2, [] )
            self.add( quest, ScenarioRace, 61, 2, [] )
            self.add( quest, ScenarioCutter, 62, 1, [pickups.Balloon] )
            self.add( quest, ScenarioCoinCollect, 63, 1, [], 10 )
            self.add( quest, ScenarioPacman, 64, 0, [] )
            self.add( quest, ScenarioBlowup, 65, 2, [] )
            self.add( quest, ScenarioRace, 66, 1, [pickups.Balloon] )
            self.add( quest, ScenarioCollectAll, 67, 2, [pickups.Dynamite] )
            self.add( quest, ScenarioHoldLamp, 68, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCoinCollect, 69, 1, [], 3 )
            self.add( quest, ScenarioPacman, 70, 0, [] )
            self.add( quest, ScenarioRace, 71, 2, [] )
            ### Oiler
            self.add( quest, ScenarioCoinCollect, 72, 1, [pickups.Oiler], 1 )
            self.add( quest, ScenarioPacman, 73, 0, [] )
            #----------------------------------------------------------------------------------centerright-bottom-hill-#
            self.add( quest, ScenarioDiamondCollect, 74, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCollectAll, 75, 1, [pickups.Oiler] )
            self.add( quest, ScenarioBlowup, 76, 2, [] )
            self.add( quest, ScenarioCoinCollect, 77, 1, [pickups.Dynamite], 3 )
            self.add( quest, ScenarioCutter, 78, 2, [pickups.Oiler] )
            self.add( quest, ScenarioDiamondCollect, 79, 1, [] )
            self.add( quest, ScenarioPacman, 80, 0, [] )
            self.add( quest, ScenarioCoinCollect, 81, 2, [pickups.Oiler], 2 )

            # -H-A-R-D-
            #
            # 109, 113, 118, 119, 120, 121, 127, 129, 130, 137, 139, 140, 141, 145, 146, 147, 151, 153, 163, 167, 171, 173, 174
            self.add( quest, ScenarioRace, 82, 2, [] )
            self.add( quest, ScenarioCollectAll, 83, 2, [pickups.Dynamite] )
            self.add( quest, ScenarioBlowup, 84, 2, [pickups.Oiler] )
            self.add( quest, ScenarioHoldLamp, 85, 2, [] )
            #-------------------------------------------------------------------------------------centerright-top-hill-#
            self.add( quest, ScenarioPacman, 86, 0, [] )
            self.add( quest, ScenarioCoinCollect, 87, 2, [pickups.Balloon], 1 )
            ### Rocks
            self.add( quest, ScenarioCollectRocks, 88, 1, [pickups.Oiler] )
            self.add( quest, ScenarioCutter, 89, 2, [pickups.Dynamite] )
            self.add( quest, ScenarioCoinCollect, 90, 1, [pickups.Oiler], 3 )
            self.add( quest, ScenarioPacman, 91, 0, [] )
            self.add( quest, ScenarioDiamondCollect, 92, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCollectRocks, 93, 1, [] )
            self.add( quest, ScenarioRace, 94, 1, [pickups.Balloon] )
            self.add( quest, ScenarioHoldLamp, 95, 2, [pickups.Oiler] )
            self.add( quest, ScenarioPacman, 96, 0, [] )
            self.add( quest, ScenarioBlowup, 97, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCollectRocks, 98, 1, [pickups.Dynamite] )
            self.add( quest, ScenarioCutter, 99, 2, [] )
            self.add( quest, ScenarioCoinCollect, 100, 2, [pickups.Oiler], 5 )
            ### Torch
            self.add( quest, ScenarioRace, 101, 1, [pickups.Torch] )
            self.add( quest, ScenarioPacman, 102, 0, [] )
            #---------------------------------------------------------------------------------------------bridge-begin-#
            self.add( quest, ScenarioHoldLamp, 103, 1, [] )
            self.add( quest, ScenarioCollectAll, 104, 1, [pickups.Torch] )
            self.add( quest, ScenarioBlowup, 105, 2, [pickups.Balloon] )
            self.add( quest, ScenarioCutter, 106, 2, [pickups.Oiler] )
            self.add( quest, ScenarioPacman, 107, 0, [] )
            self.add( quest, ScenarioDiamondCollect, 108, 1, [pickups.Torch] )
            self.add( quest, ScenarioRace, 109, 1, [] )
            self.add( quest, ScenarioBlowup, 110, 2, [pickups.Oiler] )
            self.add( quest, ScenarioCollectRocks, 111, 1, [] )
            self.add( quest, ScenarioCollectAll, 112, 1, [pickups.Dynamite] )
            self.add( quest, ScenarioCutter, 113, 2, [pickups.Torch] )
            self.add( quest, ScenarioPacman, 114, 0, [] )

            # -E-X-P-E-R-T-
            #
            #     add_level( SCENARIOXXXXXX(         TIMEOUT, GOAL, MAX, [PICKUPS],          COMPETE ), LEVEL, [A.I] ) #
            ### Ghost
            self.add( quest, ScenarioCoinCollect, 115, 1, [pickups.Ghost], 1 )
            #-----------------------------------------------------------------------------------------------bridge-end-#
            self.add( quest, ScenarioRace, 116, 2, [pickups.Balloon] )
            self.add( quest, ScenarioHoldLamp, 117, 2, [] )
            self.add( quest, ScenarioDiamondCollect, 118, 1, [pickups.Ghost] )
            self.add( quest, ScenarioPacman, 119, 0, [] )
            self.add( quest, ScenarioCollectRocks, 120, 2, [pickups.Dynamite] )
            self.add( quest, ScenarioCutter, 121, 1, [pickups.Balloon] )
            self.add( quest, ScenarioCollectAll, 122, 1, [pickups.Ghost] )
            self.add( quest, ScenarioRace, 123, 1, [] )
            self.add( quest, ScenarioCoinCollect, 124, 1, [pickups.Ghost], 3 )
            self.add( quest, ScenarioHoldLamp, 125, 2, [pickups.Balloon] )
            self.add( quest, ScenarioPacman, 126, 0, [] )
            self.add( quest, ScenarioRace, 127, 2, [pickups.Torch] )
            self.add( quest, ScenarioBlowup, 128, 2, [pickups.Oiler] )
            self.add( quest, ScenarioCutter, 129, 1, [] )
            self.add( quest, ScenarioCoinCollect, 130, 2, [pickups.Ghost], 1 )
            self.add( quest, ScenarioPacman, 131, 0, [] )
            ### Key
            self.add( quest, ScenarioCoinCollect, 132, 1, [pickups.Key], 5 )
            self.add( quest, ScenarioBlowup, 133, 2, [] )
            #-------------------------------------------------------------------------------------------right-hill-top-#
            self.add( quest, ScenarioCutter, 134, 2, [pickups.Key] )
            self.add( quest, ScenarioCollectAll, 135, 2, [pickups.Oiler] )
            self.add( quest, ScenarioCollectRocks, 136, 1, [] )
            self.add( quest, ScenarioRace, 137, 1, [pickups.Key] )
            self.add( quest, ScenarioPacman, 138, 0, [] )
            self.add( quest, ScenarioCutter, 139, 2, [pickups.Dynamite] )
            self.add( quest, ScenarioDiamondCollect, 140, 2, [] )
            self.add( quest, ScenarioHoldLamp, 141, 2, [pickups.Key] )
            self.add( quest, ScenarioBlowup, 142, 2, [pickups.Torch] )
            self.add( quest, ScenarioPacman, 143, 0, [] )
            self.add( quest, ScenarioCutter, 144, 2, [pickups.Balloon] )
            self.add( quest, ScenarioHoldLamp, 145, 2, [pickups.Key] )
            self.add( quest, ScenarioCollectAll, 146, 1, [pickups.Ghost] )
            self.add( quest, ScenarioCollectRocks, 147, 2, [pickups.Dynamite] )
            #----------------------------------------------------------------------------------------right-hill-bottom-#
            self.add( quest, ScenarioRace, 148, 2, [pickups.Torch] )
            self.add( quest, ScenarioPacman, 149, 0, [] )

            # -B-O-N-U-S-
            #
            #
            self.add( quest, ScenarioDiamondCollect, 150, 2, [pickups.Balloon] )
            self.add( quest, ScenarioBlowup, 151, 2, [pickups.Key] )
            self.add( quest, ScenarioCutter, 152, 2, [pickups.Torch] )
            self.add( quest, ScenarioCoinCollect, 153, 2, [pickups.Ghost], 1 )
            self.add( quest, ScenarioCollectAll, 154, 2, [pickups.Oiler] )

            assert len(quest.scenarios) == 155, "total level count not 155 but " + str(len(quest.scenarios))

            self._set_ais( quest, 0.1, 1.0 )


        elif quest_id == QuestManager.SINGLE_RANDOM_QUEST:
            quest = RandomQuest( 2 )

        elif quest_id == QuestManager.MULTI_RANDOM_QUEST:
            quest = RandomQuest()

        else:
            assert False, "unknown quest id"

        return quest

    def _set_ais( self, quest, stupid, smart ):
        for i in range(0, len(quest.opponent_iqs_list)):
            for j in range(0, len(quest.opponent_iqs_list[i])):
                interpol = float(i) / len(quest.opponent_iqs_list)
                quest.opponent_iqs_list[i][j] = stupid + ((smart - stupid) * interpol)

def clean_stats( stats ):
    new_stats = {}

    for key, values in stats.stats.items():
        new_stats[key] = [max(values)]

    stats.stats = new_stats

def update_stats( stats ):
    quest = QuestManager.get_instance().get_quest( QuestManager.MAIN_QUEST )

    # Load Highscores
    HIGHSCORE_FILENAME = "highscores.dic"
    highscores = {}
    if os.path.exists(HIGHSCORE_FILENAME):
        stats_file = open( HIGHSCORE_FILENAME, "rb" )
        unpickler = Unpickler( stats_file )
        highscores = unpickler.load()
        stats_file.close()

    for filename in os.listdir("other_stats"):
        if not filename.startswith("."):
            other_stats = QuestStatistics(os.path.join("other_stats", filename))

            i = 0
            for scenario in quest.scenarios:
                # no pacman scenarios
                if not isinstance( scenario, ScenarioPacman ):
                    if stats.get(i) < other_stats.get(i):
                        print "New Record: %10s: Level %03d with score %d (%s)" % (filename, i, other_stats.get(i), scenario.title)
                        stats.stats[i] = [other_stats.get(i)]
                        highscores[i] = filename

                i += 1


    score_count = {"Koen" : 0}

    # Print highscores
    print "Highscores:"
    i = 0
    for scenario in quest.scenarios:
        if highscores.has_key(i):
            print "%10s: Level %03d with score %d (%s)" % (highscores[i], i, stats.get(i), scenario.title)

            if score_count.has_key(highscores[i]):
                score_count[highscores[i]] += 1
            else:
                score_count[highscores[i]] = 1
        else:
            score_count["Koen"] += 1

        i += 1


    print "Number of Highscores:"
    for name, score in score_count.items():
        print "%10s: %3d" % (name, score)


    # Save Highscores
    stats_file = open( HIGHSCORE_FILENAME, "wb" )
    pickler = Pickler( stats_file, 2 )
    pickler.dump( highscores )
    stats_file.close()


def filter_out( stats ):
    quest = QuestManager.get_instance().get_quest( QuestManager.MAIN_QUEST )

    i = 0
    for scenario in quest.scenarios:
#        if isinstance( scenario, ScenarioHoldLamp ):
#            del stats.stats[i]

        #if i == 2:
        #    del stats.stats[i]

        #print scenario, stats.get(i)
        #assert stats.get(i) is not None
        i += 1

    #stats.stats[4] = stats.stats[5]
    #tmp = stats.stats[9]
    #stats.stats[9] = stats.stats[10]
    #stats.stats[10] = tmp
    del stats.stats[9]

if __name__ == '__main__':
    print "Quest Statistics"

    stats = QuestStatistics()

    #update_stats( stats )

    #filter_out( stats )

    clean_stats( stats )
    print stats.stats

    stats._save()

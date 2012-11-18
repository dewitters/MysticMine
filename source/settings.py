#!/usr/bin/env python

from cPickle import *
import os.path

from pygame.locals import *

import koon.input as input

from scenarios import *
from pickups import *
from player import *
import control as ctrl


class GameType (object):
    """Enum of game types"""

    TEST, SINGLE_SEQUENCE, SINGLE_RANDOM, MULTI_RANDOM = range( 4 )

class SkillLevel:

    NAMES = [_("The Best"),
             _("Expert"),
             _("Master"),
             _("Experienced"),
             _("Professional"),
             _("Amateur"),
             _("Apprentice"),
             _("Beginner")
             ]
             
    def __init__( self, value ):
        self.value = value
        self.old_value = self.value

    def  update( self, value ):
        if value is not None:
            self.old_value = self.value
            
            average = (self.value +  value) / 2

            # limit inc/dec
            INC_DEC_LIMIT = 0.25
            if average - self.value > INC_DEC_LIMIT:
                self.value += INC_DEC_LIMIT
            elif self.value - average > INC_DEC_LIMIT:
                self.value -= INC_DEC_LIMIT
            else:
                self.value = average
        
    def _get_name( self ):
        if self.value >= 1.0:
            return SkillLevel.NAMES[0]
        elif self.value >= 0.9:
            return SkillLevel.NAMES[1]
        elif self.value >= 0.8:
            return SkillLevel.NAMES[2]
        elif self.value >= 0.7:
            return SkillLevel.NAMES[3]
        elif self.value >= 0.6:
            return SkillLevel.NAMES[4]
        elif self.value >= 0.5:
            return SkillLevel.NAMES[5]
        elif self.value >= 0.4:
            return SkillLevel.NAMES[6]
        else:
            return SkillLevel.NAMES[7]
    name = property(_get_name)


class GameData:
    """Contains the data of the current game, played games, players etc.

    Public members:
    - goldcars: a list of goldcar descriptions of (name, controller)
    """

    def __init__( self, userinput ):
        self.userinput = userinput

        self.set_type( GameType.TEST )
        config = Configuration.get_instance()
        self.skill_level = SkillLevel( config.skill_level )
        self.single_player_progress = config.level_progress
        self.game_finished = False
        self.total_scores = {}

    def set_type( self, gametype ):
        self.gametype = gametype
            
        if self.gametype == GameType.SINGLE_SEQUENCE:
            self.goldcars = [["Player", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )]]
            
        elif self.gametype == GameType.SINGLE_RANDOM:
            self.goldcars = [["Player", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )]]

        elif self.gametype == GameType.MULTI_RANDOM:
#            self.goldcars = [["AI", ctrl.AiController( None )]]
            self.goldcars = [["AI", ctrl.AiController( None )], ["AJ", ctrl.AiController( None )]]
#            self.goldcars = [["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )],
#                             ["Leen", ctrl.AiController( None )],
#                             ["Computer", ctrl.AiController( None )]]
#            self.goldcars = [["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )]]
            
        else:
            self.goldcars = [["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )],
                             ["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )],
                             ["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )],
                             ["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )],
##                             ["Koen", ctrl.HumanController( None, input.Button(self.userinput.key, K_SPACE) )]]
##                             ["Leen", ctrl.AiController( None )]]
                             ["Computer", ctrl.AiController( None )]]
        #                     ["Leen", HumanController( None, input.Button(self.userinput.key, K_z) )]]

        self.scenario_nr = 0
        self.level_nr = 0 #self.scenario_nr

        quest_manager = QuestManager.get_instance()
        if self.gametype == GameType.TEST:
            self.quest = Quest()
            self.quest.add_level( ScenarioCollectAll( 120, 150, [] ), 27 )
            self.quest.add_level( ScenarioBlowup( 120, None, [Balloon], True), 8, [] )
            self.quest.add_level( ScenarioHoldLamp(       TIMEOUT, None,      [],                 True  ),   72,     [1.0, 1.0] )
            self.quest.add_level( ScenarioHoldLamp(       None,    60,        [],                 False ),   8,    [1.0, 1.0, 1.0] )

            self.quest.add_level( ScenarioCoinCollect( 120, None, 3, [] ), 39 )
            self.quest.add_level( ScenarioBlowup( 120, None, [Key] ), 86 )
            self.quest.add_level( ScenarioCoinCollect( 120, None, 1, [] ), 4 )
            self.quest.add_level( ScenarioCutter( 120, None, [Balloon] ), 1 )
            self.quest.add_level( ScenarioHoldLamp( 120, None, [Balloon] ), 6 )
            self.quest.add_level( ScenarioCoinCollect( 120, None, 20, [] ), 4 )
            self.quest.add_level( ScenarioCutter( 120, None, [] ), 1 )
            self.quest.add_level( ScenarioDiamondCollect( 120, None, 1, [] ), 6 )
            self.quest.add_level( ScenarioHoldLamp( 120, None, [] ), 6 )
#            quest.add_level( ScenarioCollectRocks( 120, 60, [] ), 4 )
#            quest.add_level( ScenarioCollectAll( 120, 150, [] ), 5 )
            self.quest.add_level( ScenarioPacman( None, 0 ), 1 )
            self.quest.add_level( ScenarioCoinCollect( 120, None, 1, [Multiplier] ), 1 )
            
        elif self.gametype == GameType.SINGLE_SEQUENCE:
            self.quest = quest_manager.get_quest( QuestManager.MAIN_QUEST )

            self.quest.progress = self.single_player_progress
            
        elif self.gametype == GameType.SINGLE_RANDOM:
            self.quest = quest_manager.get_quest( QuestManager.SINGLE_RANDOM_QUEST )
            self._fill_random_quest_items()
            self.total_scores = {}
        else:
            self.quest = quest_manager.get_quest( QuestManager.MULTI_RANDOM_QUEST )
            self._fill_random_quest_items()
            self.total_scores = {}

    def is_single_player( self ):
        """Return true if current game is single player."""
        return self.gametype == GameType.SINGLE_SEQUENCE

    def is_single_random( self ):
        return self.gametype == GameType.SINGLE_RANDOM               

    def get_quest( self ):
        """Return the current scenario."""
        return self.quest

    def save_single_player_progress( self ):
        self.single_player_progress = self.quest.progress

        config = Configuration.get_instance()
        config.level_progress = self.single_player_progress
        config.unlocked_level = max([config.unlocked_level, config.level_progress])
        config.skill_level = self.skill_level.value
        config.save()

    def _fill_random_quest_items( self ):
        available_pickups = []
        available_scenarios = [
            ScenarioCoinCollect
        ]

        config = Configuration.get_instance()

        if self.unlocked_item_count >= 1: # Diamond
            available_scenarios.append(ScenarioDiamondCollect)
            available_scenarios.append(ScenarioCollectAll)
        if self.unlocked_item_count >= 2: # Dynamite
            available_pickups.append(Dynamite)
            available_scenarios.append(ScenarioBlowup)
        if self.unlocked_item_count >= 3: # Lamp
            available_scenarios.append(ScenarioHoldLamp)
        if self.unlocked_item_count >= 4: # Balloon
            available_pickups.append(Balloon)
        if self.unlocked_item_count >= 5: # Goldcutter Axe
            available_scenarios.append(ScenarioCutter)
        if self.unlocked_item_count >= 6: # Flags
            available_scenarios.append(ScenarioRace)
        if self.unlocked_item_count >= 7: # Oiler
            available_pickups.append(Oiler)
        if self.unlocked_item_count >= 8: # Rocks
            available_scenarios.append(ScenarioCollectRocks)
        if self.unlocked_item_count >= 9: # Torch
            available_pickups.append(Torch)
        if self.unlocked_item_count >= 10: # Ghost
            available_pickups.append(Ghost)
        if self.unlocked_item_count >= 11: # Key
            available_pickups.append(Key)

        self.quest.set_available_items( available_pickups, available_scenarios )        

    def can_unlock_item( self ):
        return self._get_unlockable_item_count() > self.unlocked_item_count

    def finished_game( self ):
        return self.game_finished

    def set_game_finished( self ):
        self.game_finished = True

    def unlock_item( self ):
        config = Configuration.get_instance()
        config.unlocked_item = self.unlocked_item_count + 1
        config.save()        

    def _get_unlockable_item_count( self ):
        items = [ 3, # Diamond 
                  8, # Dynamite
                  22, # Lamp
                  33, # Balloon
                  45, # Goldcutter Axe
                  58, # Flags
                  72, # Oiler
                  88, # Rocks
                  101, # Torch
                  115, # Ghost
                  132 # Key
        ]

        config = Configuration.get_instance()

        for i in range(0, len(items)):
            if config.unlocked_level < items[i]:
                return i
        return len(items)
    
    def _get_unlocked_item_count( self ):
        return Configuration.get_instance().unlocked_item
    unlocked_item_count = property(_get_unlocked_item_count)

    def add_total_scores( self, playfield ):
        score = len( playfield.goldcars ) - 1
        for goldcars in playfield.get_goldcar_ranking():            
            for goldcar in goldcars:
                if self.total_scores.has_key( goldcar.nr ):
                    self.total_scores[goldcar.nr].score += score
                else:
                    self.total_scores[goldcar.nr] = GoldcarScore( goldcar.nr, score )

            score -= len( goldcars )

    def get_total_ranking( self ):
        """Return a sorted list of goldcars with same score"""
        single_ranking = self.total_scores.values()[:]
        single_ranking.sort( lambda a, b: cmp( b.score, a.score ) )
        
        ranking = []
        prev_score = None
        for goldcar in single_ranking:
            if prev_score is not None and goldcar.score == prev_score:
                ranking[-1].append(goldcar)
            else:
                ranking.append([goldcar])
                prev_score = goldcar.score
        
        return ranking
        
class GoldcarScore (object):
    def __init__( self, nr, score ):
        self.nr = nr
        self.score = score

class Configuration (object):
    instance = None
    config_name = os.path.expanduser("~/.mysticmine")
    
    def __init__( self ):
        """Don't call! This is a singleton!"""
        Configuration.instance = self

        self.sound_volume = 1.0
        self.music_volume = 1.0
        self.is_fullscreen = False
        self.resolution = (800, 600)

        self.level_progress = 0
        self.unlocked_level = 0
        self.unlocked_item = 0

        self.skill_level = 0.6

        self.game_speed = 1.0

        self.one_switch = False
        self.scan_speed = 30

    def _append_defaults( self ):
        default = Configuration()
        if not hasattr(self, "game_speed"):
            self.game_speed = default.game_speed
        if not hasattr(self, "one_switch"):
            self.one_switch = default.one_switch
            self.scan_speed = default.scan_speed

        Configuration.instance = self

    @staticmethod
    def get_instance():
        if Configuration.instance is None:
            if os.path.exists(Configuration.config_name):
                try:
                    Configuration.instance = Configuration.load()
                except:
                    Configuration.instance = Configuration()
            else:
                Configuration.instance = Configuration()
        return Configuration.instance
        
    def save( self ):
        config_file = open(Configuration.config_name, "wb")
        
        pickler = Pickler(config_file, 2)
        pickler.dump( self )

        config_file.close()

    @staticmethod
    def load():
        config_file = open(Configuration.config_name, "rb")
        
        unpickler = Unpickler(config_file)
        config = unpickler.load()

        config_file.close()

        config._append_defaults()

        return config
        

    

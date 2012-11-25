#!/usr/bin/env python

import os

from monorail.scenarios import *
from monorail.world import Level
from monorail.world import Playfield

class TestQuestManager:

    def test_singleton( self ):
        instance = QuestManager.get_instance()

        assert instance is not None;
        assert instance is QuestManager.get_instance()

    def test_single_player( self ):
        quest_manager = QuestManager.get_instance()
        quest = quest_manager.get_quest( QuestManager.MAIN_QUEST )

        #scenario = quest.create_scenario()

        
class TestQuest:

    def test_add_level( self ):
        quest = Quest()
        scen0 = ScenarioCoinCollect( False, 20, 1, [] )
        scen1 = ScenarioDiamondCollect( False, 20, 1, [] )
        level0 = Level()
        level1 = Level()
        quest.add_level( scen0, 0 )
        quest.add_level( scen1, 4 )

        assert quest.create_scenario() is not scen0
        assert isinstance( quest.create_scenario(), ScenarioCoinCollect )
        assert quest.get_current_level_nr() == 0

        quest.to_next_level()

        assert quest.create_scenario() is not scen1
        assert quest.get_current_level_nr() == 4

    def test_get_scenario_count( self ):
        """
        Given a quest
        When 3 scenarios are added
        Then get_scenario_count returns 3
        """
        # Given
        quest = Quest()

        # When
        quest.add_level( ScenarioCoinCollect( False, 20, 1, [] ), 1 )
        quest.add_level( ScenarioCoinCollect( False, 20, 1, [] ), 1 )
        quest.add_level( ScenarioCoinCollect( False, 20, 1, [] ), 1 )

        # Then
        assert quest.get_level_count() == 3


    def test_to_level( self ):
        """
        Given a quest with 3 levels
        When a level is selected
        Then the current scenario and level nr respond to it
        """
        # Given
        quest = Quest()
        quest.add_level( ScenarioCoinCollect( False, 20, 1, [] ), 3 )
        quest.add_level( ScenarioDiamondCollect( False, 20, 1, [] ), 4 )
        quest.add_level( ScenarioCollectRocks( 0, None, [] ), 5 )

        # When
        quest.to_level( 2 )
        # Then
        assert isinstance( quest.create_scenario(), ScenarioCollectRocks )
        assert quest.get_current_level_nr() == 5

        # When
        quest.to_level( 0 )
        # Then
        assert isinstance( quest.create_scenario(), ScenarioCoinCollect )
        assert quest.get_current_level_nr() == 3


STATNAME = "teststat"        
           
class TestStatistics:

    def setup_method(self, method):
        if os.path.exists(STATNAME):
            os.remove(STATNAME)

    def teardown_method(self, method):
        if os.path.exists(STATNAME):
            os.remove(STATNAME)

    def test_goal( self ):
        stats = QuestStatistics(STATNAME)

        stats.add( 5, 10 )
        stats.add( 9, 5 )
        stats.add( 5, 19 )
        stats.add( 5, 4 )

        assert stats.get(5) == 19
        assert stats.get(9) == 5
        assert stats.get(1) is None

    def test_save( self ):
        stats1 = QuestStatistics(STATNAME)

        stats1.add( 5, 20 )

        stats2 = QuestStatistics(STATNAME)

        assert stats2.get(5) == 20


class TestScenarioPacman:
    def test_game_tick( self ):
        scenario = ScenarioPacman(60, 60)

        playfield = Playfield()
        playfield.load("tests/levelTest.lvl")
        
        scenario.playfield = playfield

        scenario.game_tick()


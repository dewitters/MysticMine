
import os

from monorail.settings import *
from monorail.scenarios import *


class TestSettings:

    def test_init( self ):
        game_data = GameData()

    def test_is_single_player( self ):
        game_data = GameData()

        assert game_data.is_single_player() == True or \
               game_data.is_single_player() == False

    def test_get_quest( self ):
        game_data = GameData()

        print type(game_data.get_quest())
        assert isinstance( game_data.get_quest(), Quest )


class TestConfig:

    def test_save_load( self ):
        config = Configuration()

        config.sound_volume = 0.57
        config.music_volume = 0.81
        config.is_fullscreen = False

        config.save()

        config_loaded = Configuration.load()
        assert config_loaded.sound_volume == 0.57
        assert config_loaded.music_volume == 0.81
        assert config_loaded.is_fullscreen == False

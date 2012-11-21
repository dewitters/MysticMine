#!/usr/bin/env python

import sys
import os
import random
import copy
import time
import traceback
import inspect
import imp

#http://stackoverflow.com/questions/606561/how-to-get-filename-of-the-main-module-in-python
def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       # print 'Running from path', os.path.dirname(sys.executable)
       return os.path.dirname(sys.executable)
   return os.path.dirname(os.path.realpath(__file__))

script_dir = get_main_dir()

#if sys.platform == 'win32' and hasattr(sys, "frozen"):
#    script_dir = os.path.dirname(sys.executable)
#else:
#    script_dir = os.path.dirname(os.path.realpath(__file__)) 

# ----- Handling localization
import locale
import gettext
APP_NAME = "monorail"
LOCALE_DIR = os.path.join(script_dir, "data/locale")
DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES += ['en_US']
 
lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

gettext.install (True,localedir=None, unicode=1)
gettext.find(APP_NAME, mo_location)
gettext.textdomain (APP_NAME)
gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
lang = gettext.translation (APP_NAME, mo_location, languages = languages, fallback = True)
lang.install()
gettext.lang = lang
# ----- End handle localisation


import pygame
from pygame.locals import *

import koon.app
from koon.app import Game
from koon.input import UserInput, Mouse
from koon.geo import Vec3D, Vec2D, Rectangle
from koon.res import resman
from koon.gui import ImageButton, GuiState
import koon.snd as snd

from menu import MonorailMenu, SingleSwitch
from tiles import *
from world import Level, Playfield
from player import *
from hud import Hud, IngameMenu
from settings import *
from frame import Frame
from sndman import MusicManager, SoundManager
import control as ctrl
import event
import scenarios

from worldview import PlayfieldView

class Monorail (Game):
    """The Monorail main application

    public members:
    - game_is_done: True when app should exit
    """

    def __init__( self, configuration ):
        Game.__init__( self, _("Mystic Mine"), configuration )

    def before_gameloop( self ):
        resman.read("data/resources.cfg")

        self.game_data = GameData( self.userinput )

        # apply configuration settings
        SoundManager.set_sound_volume( self.config.sound_volume )
        SoundManager.set_music_volume( self.config.music_volume )

        # set state
        self.menu = MonorailMenu( self.game_data )
        self.game = MonorailGame( self.game_data )
        self.editor = None
        
        self.state = self.game
        self.state = self.menu

        # set window buttons
        self.max_button = ImageButton( copy.copy(resman.get("game.max_button")), Vec2D(800-16-4, 4) )



    def do_tick( self, indev ):
        if indev.key.is_down(K_F5) and indev.key.is_down(K_F8) and indev.key.went_down( K_ESCAPE ):
            self.game_is_done = True

        if indev.key.is_down(K_F5) and indev.key.is_down(K_F8) and indev.key.went_down( K_e ):
            if self.state == self.game:
                level_nr = self.game_data.get_quest().get_current_level_nr()
                self.editor = MonorailEditor( level_nr )
                self.state = self.editor
            elif self.state == self.editor:
                self.editor.save_all()
                self.game = MonorailGame( self.game_data )
                self.state = self.game

        if self.state == self.game:
            if self.game.is_done(): # or indev.key.went_down( K_0 ):
                self.game.to_next_level = False
                if self.game.state == MonorailGame.STATE_DONE: # or indev.key.went_down( K_0 ):
                    if self.game_data.is_single_player():
                        if self.game_data.get_quest().progress == self.game_data.get_quest().get_level_count() - 1:
                            self.game_data.set_game_finished()
                        self.game_data.get_quest().to_next_level()
                        self.game_data.save_single_player_progress()
                        self.state = self.menu
                        self.menu.show_level_select()
                    else:
                        self.game_data.get_quest().to_next_level()
                        self.game.restart( self.game_data )
                elif self.game.state == MonorailGame.STATE_MENU:
                    self.state = self.menu
                    self.menu.show_main_menu()
                elif self.game.state == MonorailGame.STATE_QUIT:
                    self.game_is_done = True
        elif self.state == self.menu:
            if self.menu.is_done():
                if self.menu.should_quit:
                    self.game_is_done = True
                else:
                    self.state = self.game
                    self.game.restart( self.game_data )
        
        self.state.do_tick( indev )

        # Handle maximize button
        self.max_button.tick( indev, None )
        if self.max_button.went_down():
            self.config.is_fullscreen = not self.config.is_fullscreen
            if not self.config.is_fullscreen:
                pygame.display.set_mode(self.config.resolution)
            else:
                pygame.display.set_mode(self.config.resolution, pygame.FULLSCREEN)

    def render( self, surface, interpol, time_sec ):
        self.state.draw( surface, interpol, time_sec )
        self.max_button.draw( surface, interpol, time_sec )
        self.state.draw_mouse( surface, interpol, time_sec )
        #self.draw_fps( surface )

            
class MonorailGame:
    STATE_INTRO, STATE_BEGIN, STATE_GAME, STATE_MENU, STATE_QUIT, STATE_STATS, STATE_TOTAL,\
                 STATE_DONE = range( 8 )

    MOUSE_TIMEOUT = 25 * 3
    
    def __init__( self, game_data ):
        self.restart( game_data )
        self.music_man = MusicManager()
        
        # preload clock sounds and big explosion graphic
        resman.get("game.clock_sound")
        resman.get("game.clockring_sound")
        resman.get("game.explosion_sprite")


    def restart( self, game_data ):
        """Start a new game with the current game_data"""
        self.game_data = game_data
        
        self.state = MonorailGame.STATE_INTRO
        
        self.scenario = self.game_data.get_quest().create_scenario(self.game_data.skill_level.value)
        self.playfield = self.scenario.playfield
        self.controller = ctrl.GroundControl( self.playfield )
        self.init_goldcars()
       
        self.hud = Hud( self.scenario, self.controller, self.game_data )
        self.hud.start_intro_screen()
        
        self.begin_timeout = 25 * 3

        self.ingame_menu = None
        self.gui_state = GuiState()
        
        self.mouse_timeout = MonorailGame.MOUSE_TIMEOUT
        self.is_paused = False

    def init_goldcars( self ):
        goldcar_names = []
        controllers = []
        for name, controller in self.game_data.goldcars:
            goldcar_names.append( name )
            controllers.append( controller )

        for iq in self.game_data.get_quest().get_opponent_iqs():
            goldcar_names.append( "" )
            controllers.append( ctrl.AiController( None, iq ) )
            
        self.playfield.add_goldcars( goldcar_names )
        self.controller.add_controllers( controllers )        
            
    def do_tick( self, indev ):
        if self.ingame_menu is None and not self.is_paused:
            if self.game_data.is_single_player() or \
                        self.game_data.is_single_random():
                SingleSwitch.feed_keys( indev )

                # in singleplayer, all joystick buttons are keypress
                for joy in indev.joys:
                    if joy.any_went_down():
                        indev.key.feed_down( K_SPACE )
                    if joy.any_went_up():
                        indev.key.feed_up( K_SPACE )

            
            if self.state == MonorailGame.STATE_INTRO:
                if self.hud.is_ready(): # or self.game_data.is_single_player():
                    self.hud.end_info()
                    self.state = MonorailGame.STATE_BEGIN
                    self.music_man.play()

            elif self.state == MonorailGame.STATE_BEGIN:
                if self.begin_timeout % 50 == 0:
                    random_spawn = not self.game_data.is_single_player();
                    spawns_left = self.playfield.spawn_next_goldcar( random_spawn )
                    if spawns_left:
                        self.begin_timeout += 50

                self.controller.game_tick( indev )
                self.playfield.game_tick()

                # Start right away in single player
                if self.game_data.is_single_player():
                    self.scenario.game_tick()
                
                self.begin_timeout -= 1
                if self.begin_timeout <= 0:            
                    self.state = MonorailGame.STATE_GAME

                if indev.mouse.has_moved():
                    self.mouse_timeout = MonorailGame.MOUSE_TIMEOUT
                else:
                    self.mouse_timeout -= 1                
            
            elif self.state == MonorailGame.STATE_GAME:
                self.controller.game_tick( indev )
                self.playfield.game_tick()
                self.scenario.game_tick()
                if self.scenario.is_finished():
                    if not self.game_data.is_single_player():
                        self.hud.start_end_screen()
                    else:
                        self.game_data.get_quest().save_score( self.scenario )
                        skill = self.game_data.get_quest().get_skill( self.scenario )
                        self.game_data.skill_level.update( skill )
                        
                        self.game_data.save_single_player_progress()

                        if self.scenario.has_won():
                            self.hud.start_win_screen()
                        else:
                            self.hud.start_lose_screen()
                            
                    self.state = MonorailGame.STATE_STATS
                    self.mouse_timeout = MonorailGame.MOUSE_TIMEOUT
                    self.music_man.stop()

                if indev.mouse.has_moved():
                    self.mouse_timeout = MonorailGame.MOUSE_TIMEOUT
                else:
                    self.mouse_timeout -= 1

            elif self.state == MonorailGame.STATE_STATS:
                if self.hud.is_ready():
                    if not self.game_data.is_single_player():
                        self.game_data.add_total_scores( self.playfield )
                        self.hud.start_total_screen()
                        self.state = MonorailGame.STATE_TOTAL
                    else:
                        if self.scenario.has_won():
                            self.state = MonorailGame.STATE_DONE
                        else:
                            self.restart( self.game_data )
                            return
                                        
            elif self.state == MonorailGame.STATE_TOTAL:
                if self.hud.is_ready():
                    self.state = MonorailGame.STATE_DONE

            elif self.state == MonorailGame.STATE_MENU:
                pass
                                    
            self.hud.game_tick( indev )
            self.music_man.game_tick()

            SingleSwitch.tick( indev, None )
            if indev.key.went_down( K_ESCAPE ) or \
                        self.hud.menu_btn.went_down() or \
                        SingleSwitch.esc_went_down:
                resman.get("gui.paper_sound").play()                
                self.ingame_menu = IngameMenu(self.game_data.is_single_player(), self.game_data)                
            
        elif self.ingame_menu is not None: # Ingame Menu
            SingleSwitch.feed_keys( indev )

            self.gui_state.update( indev, self.ingame_menu )
            self.ingame_menu.tick( indev, self.gui_state )

            if self.ingame_menu.is_done():
                if self.ingame_menu.to_menu:
                    self.music_man.stop()
                    self.state = MonorailGame.STATE_MENU
                elif self.ingame_menu.should_quit:
                    self.music_man.stop()
                    self.state = MonorailGame.STATE_QUIT
                elif self.ingame_menu.to_next_level:
                    self.music_man.stop()
                    self.state = MonorailGame.STATE_DONE
                    
                self.ingame_menu = None

            self.mouse_timeout = MonorailGame.MOUSE_TIMEOUT

#        if indev.key.went_down( K_p ):
#            self.is_paused = not self.is_paused

        event.Event.update()

        # for debugging
        if self.is_paused:
            self.controller.game_tick( indev )


    def draw( self, surface, interpol, time_sec ):
        #surface.fill( (0,0,0) )
        
        frame = Frame( surface, time_sec, interpol )
        if self.ingame_menu is not None or self.is_paused or\
            self.state not in [MonorailGame.STATE_BEGIN, MonorailGame.STATE_GAME]:
            frame.interpol = 0.0
        frame.draw( self.playfield )
        frame.draw( self.controller )

        self.hud.draw( frame )

        if self.ingame_menu is not None:
            self.ingame_menu.draw( surface )

        frame.draw( event.Event.instance )

    def draw_mouse( self, surface, interpol, time_sec ):
        if self.mouse_timeout > 0:
            x, y = pygame.mouse.get_pos()
            resman.get("gui_surf").draw( surface, Vec2D(x, y), (0,0,32,32) )            

    def mouse_down( self, button ):
        pass

    def is_done( self ):
        return self.state == MonorailGame.STATE_DONE \
               or self.state == MonorailGame.STATE_MENU \
               or self.state == MonorailGame.STATE_QUIT


class MonorailEditor:
    FLAT, NORTH_SLOPE, EAST_SLOPE, SOUTH_SLOPE, WEST_SLOPE, ENTERANCE,\
    ERASE, MAX = range( 8 )

    X_OFFSET, Y_OFFSET = 20, 300
    
    def __init__( self, level_nr ):
        self.level_nr = level_nr
        self.load_level()
        self.current_tile = MonorailEditor.FLAT
        self.update_edit_tiles()

    def load_level( self ):
        self.level = Level()
        if os.path.exists( Level.get_filename( self.level_nr ) ):
            self.level.load( Level.get_filename( self.level_nr ) )        

    def save_all( self ):
        self.level.save( Level.get_filename( self.level_nr ) )

    def do_tick( self, indev ):
        self.update_tiles()
        self.update_edit_tiles()

        if pygame.mouse.get_pressed()[0]: # Left mouse button
            if self.current_tile in [MonorailEditor.FLAT, MonorailEditor.ENTERANCE]:
                self.level.set_tile( self.edit_tile1 )
            elif self.current_tile in [MonorailEditor.NORTH_SLOPE, MonorailEditor.EAST_SLOPE, MonorailEditor.SOUTH_SLOPE, MonorailEditor.WEST_SLOPE]:
                self.level.set_tile( self.edit_tile1 )
                self.level.set_tile( self.edit_tile2 )
            elif self.current_tile == MonorailEditor.ERASE:
                self.level.remove_tile( self.edit_tile1.pos.x, self.edit_tile1.pos.y )


        if indev.key.went_down( K_PAGEUP ):
            if self.level_nr > 0:
                self.save_all()
                self.level_nr -= 1
                self.load_level()            
        elif indev.key.went_down( K_PAGEDOWN ):
            self.save_all()
            self.level_nr += 1
            self.load_level()

        if indev.key.went_down( K_UP ):
            for tile in self.level.tiles:
                tile.pos.y -= 1
        if indev.key.went_down( K_DOWN ):
            for tile in self.level.tiles:
                tile.pos.y += 1
        if indev.key.went_down( K_LEFT ):
            for tile in self.level.tiles:
                tile.pos.x -= 1
        if indev.key.went_down( K_RIGHT ):
            for tile in self.level.tiles:
                tile.pos.x += 1
                

    def draw( self, surface, interpol, time_sec ):
        surface.fill( (50,50,50) )

        #resman.get("game.hud_left_surf").draw( surface, Vec2D(0,0) )

        
        frame = Frame( surface, time_sec, interpol )
        frame.X_OFFSET = MonorailEditor.X_OFFSET
        frame.Y_OFFSET = MonorailEditor.Y_OFFSET
        frame.draw_z( [self.level] )

        if self.current_tile in [MonorailEditor.FLAT, MonorailEditor.ENTERANCE]:
            frame.draw( self.edit_tile1 )
            
        elif self.current_tile in [MonorailEditor.NORTH_SLOPE ,MonorailEditor.EAST_SLOPE, MonorailEditor.SOUTH_SLOPE, MonorailEditor.WEST_SLOPE]:
            frame.draw( self.edit_tile1 )
            frame.draw( self.edit_tile2 )
            
        elif self.current_tile == MonorailEditor.ERASE:
            pass

        # draw filename
        font = pygame.font.Font( None, 24 )
        render_text = font.render( Level.get_filename( self.level_nr ), 0, (255,255,255) )
        surface.blit( render_text, (100,10) )

    def draw_mouse( self, surface, interpol, time_sec ):
        x, y = pygame.mouse.get_pos()
        resman.get("gui_surf").draw( surface, Vec2D(x, y), (0,0,32,32) )


    def mouse_down( self, button ):
        if button == 4: # Wheel up
            self.current_tile = (self.current_tile+MonorailEditor.MAX-1) % MonorailEditor.MAX
        if button == 5: # Wheel down
            self.current_tile = (self.current_tile+1) % MonorailEditor.MAX

        self.update_edit_tiles()

    def update_edit_tiles( self ):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        pos = Vec3D((-mouse_y + (mouse_x+32)/2 - MonorailEditor.X_OFFSET/2 + MonorailEditor.Y_OFFSET) / 32,
    	            (mouse_y + (mouse_x-32)/2 - MonorailEditor.X_OFFSET/2 - MonorailEditor.Y_OFFSET) / 32,
                     0)

        if self.current_tile == MonorailEditor.FLAT:
            self.edit_tile1 = Tile( pos, Tile.Type.FLAT )
        elif self.current_tile == MonorailEditor.NORTH_SLOPE:
            self.edit_tile1 = Tile( pos, Tile.Type.NORTH_SLOPE_TOP )
            pos += Vec3D(-1,0,0)
            self.edit_tile2 = Tile( pos, Tile.Type.NORTH_SLOPE_BOT )
        elif self.current_tile == MonorailEditor.EAST_SLOPE:
            self.edit_tile1 = Tile( pos, Tile.Type.EAST_SLOPE_TOP )
            pos += Vec3D(0,1,0)
            self.edit_tile2 = Tile( pos, Tile.Type.EAST_SLOPE_BOT )
        elif self.current_tile == MonorailEditor.SOUTH_SLOPE:
            self.edit_tile1 = Tile( pos, Tile.Type.SOUTH_SLOPE_TOP )
            pos += Vec3D(-1,2,0)
            self.edit_tile2 = Tile( pos, Tile.Type.SOUTH_SLOPE_BOT )
        elif self.current_tile == MonorailEditor.WEST_SLOPE:
            self.edit_tile1 = Tile( pos, Tile.Type.WEST_SLOPE_TOP )
            pos += Vec3D(-2,1,0)
            self.edit_tile2 = Tile( pos, Tile.Type.WEST_SLOPE_BOT )
        elif self.current_tile == MonorailEditor.ENTERANCE:
            self.edit_tile1 = Enterance( pos )
        #elif self.current_tile == MonorailEditor.RAILGATE:
        #    self.edit_tile1 = RailGate( pos )
        elif self.current_tile == MonorailEditor.ERASE:
            self.edit_tile1 = Tile( pos, Tile.Type.FLAT )
            pass

    def update_tiles( self ):
        for tile in self.level.tiles:
            tile.pickup = None
            tile.set_selected( tile.is_switch() )

def main():
    args = []
    for arg in sys.argv:
        args.append( arg.lower() )

    # Change current working dir to script directory
    os.chdir( script_dir )

    configuration = Configuration.get_instance()
    #configuration.is_fullscreen = "fullscreen" in args
    SingleSwitch.is_enabled = ("ss" in args) or configuration.one_switch
    SingleSwitch.scan_timeout = configuration.scan_speed
    
    koon.app.set_game_speed(configuration.game_speed)

    app = Monorail( configuration )
    app.run()


    # Make sure latest configuration gets saved
    configuration.save()

if __name__ == '__main__':
    try:
        main()
    except BaseException, e:
        log = open("error_mm.log", "a")
        log.write("\n------- " + time.strftime("%a %b %d %Y %H:%M:%S") + "\n")
        log.write(traceback.format_exc())
        log.write("\n")
        log.close()
        raise



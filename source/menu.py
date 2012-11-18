#!/usr/bin/env python

import math
import random

import pygame
from pygame.locals import *

import koon.app
from koon.gui import *
from koon.geo import *
from koon.res import resman
import koon.gfx as gfx
import koon.input as input

from settings import GameType, Configuration
from player import *
from sndman import SoundManager
import scenarios
import control as ctrl
import pickups

class MonorailMenu:
    def __init__( self, game_data ):
        self.game_data = game_data
        self.screen = ScreenGameSelect( game_data )
        self._is_done = False
        self.should_quit = False
        self.guistate = GuiState()
        self.music = resman.get("game.menu_music")
        self.music.play( -1 )

    def do_tick( self, userinput ):
        SingleSwitch.feed_keys( userinput )
        SingleSwitch.check_enable( userinput )

        self.screen.tick( userinput, self.guistate )

        if isinstance( self.screen, ScreenGameSelect ):
            if self.screen.is_done():
                if self.screen.should_quit:
                    self.should_quit = True
                    self._is_done = True
                elif self.game_data.is_single_player():
                    self.screen = ScreenLevelSelect( self.game_data )
                elif self.game_data.is_single_random():
                    self._is_done = True
                else:
                    self._is_done = True
                    # self.screen = ScreenPlayerSelect( self.game_data )
                    
        elif isinstance( self.screen, ScreenLevelSelect ):
            if self.screen.is_done():
                if self.screen.get_state() == ScreenLevelSelect.PLAY:
                    self._is_done = True
                elif self.screen.get_state() == ScreenLevelSelect.MENU:
                    self.screen = ScreenGameSelect( self.game_data )
                    
        elif isinstance( self.screen, ScreenPlayerSelect ):
            if self.screen.is_done():
                self._is_done = True

        if self._is_done:
            self.music.fadeout( 1000 )

    def show_level_select( self ):
        self.screen = ScreenLevelSelect( self.game_data )
        self._is_done = False
        self.music.play()

    def show_main_menu( self ):
        self.screen = ScreenGameSelect( self.game_data )
        self._is_done = False
        self.music.play()

    def draw( self, surface, interpol, time_sec ):
        surface.fill( (0,0,0) )

        self.screen.draw( surface, interpol, time_sec )

    def draw_mouse( self, surface, interpol, time_sec ):
        x, y = pygame.mouse.get_pos()
        resman.get("gui_surf").draw( surface, Vec2D(x, y), (0,0,32,32) )            


    def mouse_down( self, button ):
        pass

    def is_done( self ):
        return self._is_done

class Credit:
    FONT = None
    FONT_BLACK = None

    def __init__( self, text ):
        self.text = text
        self.pos = Vec2D( 0, 0 )
        self.speed = -10

        if Credit.FONT is None:
            Credit.FONT = Font( "data/edmunds.ttf", color=(255,255,255), size=25, use_antialias = True )        
            Credit.FONT_BLACK = Font( "data/edmunds.ttf", color=(0,0,0), size=25, use_antialias = True )        

    def tick( self ):
        self.speed += 0.3
        self.pos.x += 3
        self.pos.y += self.speed

    def is_dead( self ):
        return self.pos.y > -90 and self.speed > 0

    def draw( self, surface, offset_x ):
        Credit.FONT_BLACK.draw( self.text, surface, (172 + int(self.pos.x), int(self.pos.y) + offset_x + 602), Font.CENTER )
        Credit.FONT.draw( self.text, surface, (170 + int(self.pos.x), int(self.pos.y) + offset_x + 600), Font.CENTER )

class CarAnimation:
    
    class RailObject:
        def __init__( self, weight ):
            self.weight = weight
            self.offset = 0.0
            self.speed = 0.0

        def tick( self, parent_offset ):
           if self.offset > parent_offset:
                if self.offset - 5 > parent_offset:
                    self.offset = parent_offset + 5
                self.speed -= (self.weight * 1)
                self.offset += self.speed
                if self.offset <= parent_offset:
                    self.speed = 0.0
                    self.offset = parent_offset
           elif self.offset < parent_offset: 
                self.speed += self.weight
                self.offset += self.speed
                if self.offset >= parent_offset:
                    self.speed = 0.0
                    self.offset = parent_offset


    STATE_NORMAL, STATE_DOWN, STATE_UP, STATE_CREDITS = range(4)

    CREDITS = [line for line in """-= Created by =-
    Koonsolo
    www.koonsolo.com

    -= Programming =-
    Koen Witters

    -= Graphics =-
    Koen Witters

    -= Music =-
    Jeremy Sherman
    Heartland

    -= Thanks to =-
    Roel Guldentops
    Leen Vander Kuylen
    Maarten Vander Kuylen
    William Van Haevre
    Michael Van Loock
    Nick Verhaert
    Erik Wollebrants

    -= Tools Used =-
    Python
    Pygame
    Blender
    The Gimp
    Vim
    Kubuntu
    Audacity
    """.splitlines()]

    def __init__( self ):
        self.carsprite = resman.get("game.introcar_sprite")
        self.carsprite_car = resman.get("game.introcar_car")
        self.carsprite_man = resman.get("game.introcar_man")
        self.carsprite_hat = resman.get("game.introcar_hat")
        self.carsprite_hat_front = resman.get("game.introcar_hat_front")
        self.rails = CarAnimation.RailObject( 0 )
        self.car = CarAnimation.RailObject( 1.5 )
        self.man = CarAnimation.RailObject( 1.0 )
        self.hat = CarAnimation.RailObject( 1.0 )

        self.credits = []
        self.credits_counter = 0
        self.credits_index = 0

        self.state = CarAnimation.STATE_NORMAL

    def tick( self, userinput ):
        self.tick_car( userinput )

        # check click on hat
        if userinput.mouse.went_down( input.Mouse.LEFT )\
           and Rectangle(150, self.hat.offset + 150, 155, 50).contains(userinput.mouse.pos):
            resman.get("gui.shot_sound").play()
            self.state = CarAnimation.STATE_DOWN

        if self.state == CarAnimation.STATE_CREDITS:
            self.credits_counter += 1
            if self.credits_counter > 25:
                self.credits_counter = 0
                self.credits.append( Credit( CarAnimation.CREDITS[ self.credits_index ] ) )
                self.credits_index = (self.credits_index + 1) % len(CarAnimation.CREDITS)

            new_credits = []
            for credit in self.credits:
                credit.tick()
                if not credit.is_dead():
                    new_credits.append( credit )
            self.credits = new_credits
        
    def tick_car( self, userinput ):
        self.carsprite.nr = (self.carsprite.nr + 1) % 5
        
        if self.state == CarAnimation.STATE_DOWN:
            offset = 400
            if self.rails.offset >= 400:
                self.state = CarAnimation.STATE_UP
        elif self.state == CarAnimation.STATE_UP:
            offset = -150
            if self.rails.offset <= -150:
                self.state = CarAnimation.STATE_CREDITS
        elif self.state == CarAnimation.STATE_CREDITS:
            offset = -150
            self.rails.offset = -150
        else:
            offset = random.randint(-200, 105)


        if self.rails.offset > offset:
            self.rails.speed -= 4.7
        else:
            self.rails.speed += 4.7

        self.rails.speed = max((min((self.rails.speed,8)), -8))
        self.rails.offset += self.rails.speed

        self.car.tick( self.rails.offset )
        self.man.tick( self.car.offset )
        self.hat.tick( self.man.offset )

    def draw( self, surface, interpol, time_sec ):
        if self.state == CarAnimation.STATE_CREDITS:
            self.draw_credits( surface, False )

        self.carsprite.draw( surface, Vec2D(-150, 80 + self.rails.offset) )
        if self.state == CarAnimation.STATE_NORMAL or self.state == CarAnimation.STATE_DOWN:
            if self.state == CarAnimation.STATE_NORMAL:
                self.carsprite_hat.draw( surface, Vec2D(-150, 80 + self.hat.offset) )
            self.carsprite_man.draw( surface, Vec2D(-150, 80 + self.man.offset) )
            if self.state == CarAnimation.STATE_NORMAL:
                self.carsprite_hat_front.draw( surface, Vec2D(-150, 80 + self.hat.offset) )
            self.carsprite_car.draw( surface, Vec2D(-150, 80 + self.car.offset) )

        if self.state == CarAnimation.STATE_CREDITS:
            self.draw_credits( surface, True )

    def draw_credits( self, surface, is_on_top ):
        for credit in self.credits:
            if credit.speed >= 0 and not is_on_top:
                credit.draw( surface, self.rails.offset )
            if credit.speed < 0 and is_on_top:
                credit.draw( surface, self.rails.offset )

class SingleSwitch:
    is_enabled = False
    next_cnt = 0
    esc_timers = {}
    esc_went_down = False

    scan_timeout = 60

    @staticmethod
    def tick( indev, guistate ):
        if SingleSwitch.is_enabled:
            if indev.any_went_down():
                SingleSwitch.next_cnt = 0

            SingleSwitch.next_cnt += 1
            if SingleSwitch.next_cnt >= SingleSwitch.scan_timeout:
                SingleSwitch.next_cnt = 0
                if guistate is not None:
                    guistate.activate_next()

            # Remove non down buttons
            new_timers = {}
            for key, value in SingleSwitch.esc_timers.items():
                if key.button in key.dev.down_buttons:
                    new_timers[ key ] = value
            SingleSwitch.esc_timers = new_timers

            # Add buttons
            SingleSwitch.esc_went_down = False
            for dev in indev.devs_no_mouse:
                for key in dev.down_buttons:
                    btn = input.Button( dev, key )
                    if SingleSwitch.esc_timers.has_key( btn ):
                        SingleSwitch.esc_timers[ btn ] += 1
                    else:
                        SingleSwitch.esc_timers[ btn ] = 1

                    if SingleSwitch.esc_timers[ btn ] == 25:
                        SingleSwitch.esc_went_down = True
        
    @staticmethod
    def feed_keys( indev ):
        if SingleSwitch.is_enabled:
            if indev.any_went_down():
                if K_SPACE not in indev.key.went_down_buttons:
                    indev.key.feed_down( K_SPACE )
            if indev.any_went_up():
                if K_SPACE not in indev.key.went_up_buttons:
                    indev.key.feed_up( K_SPACE )

    @staticmethod
    def check_enable( indev ):
        if not SingleSwitch.is_enabled:
            # Remove non down buttons
            new_timers = {}
            for key, value in SingleSwitch.esc_timers.items():
                if key.button in key.dev.down_buttons:
                    new_timers[ key ] = value
            SingleSwitch.esc_timers = new_timers

            # Add buttons
            SingleSwitch.esc_went_down = False
            for dev in indev.devs_no_mouse:
                for key in dev.down_buttons:
                    btn = input.Button( dev, key )
                    if SingleSwitch.esc_timers.has_key( btn ):
                        SingleSwitch.esc_timers[ btn ] += 1
                    else:
                        SingleSwitch.esc_timers[ btn ] = 1

                    if SingleSwitch.esc_timers[ btn ] == 25 * 3:
                        SingleSwitch.is_enabled = True

class ScreenGameSelect (Screen):


    def __init__( self, game_data ):
        super(type(self), self).__init__()

        self.game_data = game_data
        self._is_done = False
        self.should_quit = False
        
        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=30, use_antialias = True )        
        
        BUTTON_X = 550
        BUTTON_Y = 180
        H = 65

        self.adventure_btn = ImageButton( copy.copy(resman.get("game.button01_sprite")), Vec2D(BUTTON_X, BUTTON_Y) )
        self.adventure_btn.set_label(_("Adventure"), btnFont )
        self.quick_play  = ImageButton( copy.copy(resman.get("game.button01_sprite")), Vec2D(BUTTON_X, BUTTON_Y + H) )
        self.quick_play.set_label( _("Quick play"), btnFont )
        self.multiplayer_btn  = ImageButton( copy.copy(resman.get("game.button01_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 2*H) )
        self.multiplayer_btn.set_label( _("Multiplayer"), btnFont )
        self.options_btn  = ImageButton( copy.copy(resman.get("game.button01_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 3*H) )
        self.options_btn.set_label( _("Options"), btnFont )
        self.quit_btn  = ImageButton( copy.copy(resman.get("game.button01_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 4*H) )
        self.quit_btn.set_label( _("Quit"), btnFont )

        if Configuration.get_instance().unlocked_level == 0:
            self.quick_play.is_enabled = False
            self.multiplayer_btn.is_enabled = False

        self.add_subcomponent( self.adventure_btn )
        self.add_subcomponent( self.quick_play )
        self.add_subcomponent( self.multiplayer_btn )
        self.add_subcomponent( self.options_btn )
        self.add_subcomponent( self.quit_btn )

        self.update_neighbors()

        self.dialog = None

        self.background = resman.get("gui.logo_surf")

        self.crate_hud = CrateHud( game_data )
        self.car_animation = CarAnimation()

    def tick( self, userinput, guistate ):
        if self.dialog is None:
            super(type(self), self).tick( userinput, guistate )

            if self.adventure_btn.went_down():
                Event.button()
                self.game_data.set_type( GameType.SINGLE_SEQUENCE )
                self._is_done = True
            elif self.quick_play.went_down():
                Event.button()
                self.game_data.set_type( GameType.SINGLE_RANDOM )
                self._is_done = True
            elif self.multiplayer_btn.went_down():
                Event.button()
                self.dialog = ScreenPlayerSelect(self.game_data)
                self.add_subcomponent( self.dialog )
                self.game_data.set_type( GameType.MULTI_RANDOM )
                self._is_enabled = False
            elif self.options_btn.went_down():
                Event.button()
                self.dialog = OptionsDialog(self.game_data)
                self.add_subcomponent( self.dialog )
                self.is_enabled = False
            elif self.quit_btn.went_down():
                Event.button()
                self.should_quit = True
                self._is_done = True

            SingleSwitch.tick( userinput, guistate )

        else:
            self.dialog.tick( userinput, guistate )

            if self.dialog.is_done():
                if isinstance(self.dialog, ScreenPlayerSelect) and \
                   not self.dialog.cancelled:
                    self._is_done = True
                self.remove_subcomponent( self.dialog )
                self.dialog = None
                self.is_enabled = True

        self.crate_hud.tick()
        self.car_animation.tick( userinput )

    def draw( self, surface, interpol, time_sec ):
        self.background.draw( surface, (0, 0) )

        self.car_animation.draw( surface, interpol, time_sec )

        self.crate_hud.draw( surface )

        Screen.draw( self, surface, interpol, time_sec )

        
            
    def is_done( self ):
        return self._is_done

class OptionsDialog (Dialog):

    def __init__( self, game_data ):
        super(type(self), self).__init__( Rectangle(140, 80, 800-200, 600-200 ) )
        self.background_image = resman.get("gui.paperdialog_surf")
        self._is_done = False
        self.game_data = game_data

        self.dialog = None

        self.config = Configuration.get_instance()

        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )

        self.sound_lbl = Label( Vec2D(200, 130), _("Sound"), btnFont )
        star = ImageButton( copy.copy(resman.get("gui.sheriffstar_sprite") ) )
        self.sound_slider = ImageSlider( Vec2D( 320, 140 ), copy.copy(resman.get("gui.slider_sprite")), star )
        self.music_lbl = Label( Vec2D(200, 195), _("Music"), btnFont )        
        star = ImageButton( copy.copy(resman.get("gui.sheriffstar_sprite") ) )
        self.music_slider = ImageSlider( Vec2D( 320, 205 ), copy.copy(resman.get("gui.slider_sprite")), star )
        self.fullscreen_btn = ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(300,260) )
        self.update_fullscreen_label()
        self.access_btn = ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(300,340) )
        self.access_btn.set_label( _("Accessibility"), btnFont )
        self.close_btn = ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(300,420) )
        self.close_btn.set_label( _("Close"), btnFont )

        self.add_subcomponent( self.sound_lbl )
        self.add_subcomponent( self.sound_slider )
        self.add_subcomponent( self.music_lbl )
        self.add_subcomponent( self.music_slider )
        self.add_subcomponent( self.fullscreen_btn )
        self.add_subcomponent( self.access_btn )
        self.add_subcomponent( self.close_btn )

        self.sound_slider.set_value( SoundManager.get_sound_volume() )
        self.music_slider.set_value( SoundManager.get_music_volume() )

        self.update_neighbors()

    def tick( self, userinput, guistate ):
        if self.dialog is None:
            Dialog.tick( self, userinput, guistate )
            if self.close_btn.went_down():
                Event.button()
                self._is_done = True
            if self.access_btn.went_down():
                self.dialog = AccessDialog(self.game_data)
                self.add_subcomponent( self.dialog )
                self.is_enabled = False
            if self.fullscreen_btn.went_down():
                Event.button()
                self.config.is_fullscreen = not self.config.is_fullscreen
                if not self.config.is_fullscreen:
                    pygame.display.set_mode(self.config.resolution)
                else:
                    pygame.display.set_mode(self.config.resolution, pygame.FULLSCREEN)
                self.update_fullscreen_label()

            if self.sound_slider.value_changed():
                self.config.sound_volume = self.sound_slider.get_value()
                SoundManager.set_sound_volume( self.config.sound_volume )
            if self.sound_slider.went_up():
                Event.sound_test()
            if self.music_slider.value_changed():
                self.config.music_volume = self.music_slider.get_value()            
                SoundManager.set_music_volume(  self.config.music_volume )
                    
            SingleSwitch.tick( userinput, self.guistate )
        else:
            self.dialog.tick( userinput, guistate )

            if self.dialog.is_done():
                self.remove_subcomponent( self.dialog )
                self.dialog = None
                self.is_enabled = True

    def update_fullscreen_label( self ):
        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )
        if self.config.is_fullscreen:
            self.fullscreen_btn.set_label( _("Windowed"), btnFont )
        else:
            self.fullscreen_btn.set_label( _("Fullscreen"), btnFont )

    def is_done( self ):
        self.config.save()
        return self._is_done

class AccessDialog (Dialog):

    def __init__( self, game_data ):
        Dialog.__init__( self, Rectangle(140, 80, 800-200, 600-200 ) )
        self.background_image = resman.get("gui.paperdialog_surf")
        self._is_done = False
        self.game_data = game_data

        self.config = Configuration.get_instance()

        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )

        # Game speed, Scroll speed, Single Button mode
        self.speed0_lbl = Label( Vec2D(200, 140), _("Game"), btnFont )
        self.speed1_lbl = Label( Vec2D(200, 170), _("Speed"), btnFont )
        star = ImageButton( copy.copy(resman.get("gui.sheriffstar_sprite") ) )
        self.speed_slider = ImageSlider( Vec2D( 320, 170 ), copy.copy(resman.get("gui.slider_sprite")), star )

        self.oneswitch_btn = ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(300,240) )
        self.update_oneswitch_label()

        self.scan0_lbl = Label( Vec2D(200, 310), _("Scan"), btnFont )        
        self.scan1_lbl = Label( Vec2D(200, 340), _("Speed"), btnFont )        
        star = ImageButton( copy.copy(resman.get("gui.sheriffstar_sprite") ) )
        self.scan_slider = ImageSlider( Vec2D( 320, 340 ), copy.copy(resman.get("gui.slider_sprite")), star )

        self.close_btn = ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(300,400) )
        self.close_btn.set_label( _("Close"), btnFont )

        self.add_subcomponent( self.speed0_lbl )
        self.add_subcomponent( self.speed1_lbl )
        self.add_subcomponent( self.speed_slider )
        self.add_subcomponent( self.oneswitch_btn )
        self.add_subcomponent( self.scan0_lbl )
        self.add_subcomponent( self.scan1_lbl )
        self.add_subcomponent( self.scan_slider )
        self.add_subcomponent( self.close_btn )

        self.speed_slider.set_value( self.config.game_speed )
        self.scan_slider.set_value( 1.0 - ((self.config.scan_speed - 20) / float(40)) )

        self.update_neighbors()

    def tick( self, userinput, guistate ):
        Dialog.tick( self, userinput, guistate )
        if self.close_btn.went_down():
            Event.button()
            self._is_done = True
        if self.oneswitch_btn.went_down():
            Event.button()
            SingleSwitch.is_enabled = not SingleSwitch.is_enabled
            self.config.one_switch = SingleSwitch.is_enabled
            self.update_oneswitch_label()

        if self.speed_slider.value_changed():
            self.config.game_speed = lin_ipol(self.speed_slider.get_value(), 0.4, 1.0)
            koon.app.set_game_speed(self.config.game_speed)
        if self.scan_slider.value_changed():
            SingleSwitch.scan_timeout = int(20 + (1.0 - self.scan_slider.get_value()) * 40)
            self.config.scan_speed = SingleSwitch.scan_timeout
                
        SingleSwitch.tick( userinput, self.guistate )

    def update_oneswitch_label( self ):
        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )
        if not SingleSwitch.is_enabled:
            self.oneswitch_btn.set_label( _("One Switch"), btnFont )
        else:
            self.oneswitch_btn.set_label( _("Normal Mode"), btnFont )

    def is_done( self ):
        self.config.save()
        return self._is_done


class ScreenPlayerSelect (Dialog):

    def __init__( self, game_data ):
        super(ScreenPlayerSelect, self).__init__( Rectangle(140, 80, 800-200, 600-200 ) )
        self.background_image = resman.get("gui.paperdialog_surf")

        self.game_data = game_data
        self._is_done = False
        self.cancelled = False

        self.stage = StageHumanCount()

    def tick( self, userinput, guistate ):
        super(type(self), self).tick( userinput, guistate )

        self.stage.tick( userinput, guistate )

        if isinstance( self.stage, StageHumanCount ):
            cnt = self.stage.get_player_count()
            if cnt is not None:
                if cnt != -1:
                    self.stage = StagePlayerConfig( self.game_data, cnt )
                else:
                    self.cancelled = True
                    self._is_done = True
        if isinstance( self.stage, StagePlayerConfig ):
            if self.stage.is_done():
                self._is_done = True

    def draw( self, surface, interpol, time_sec ):
        Dialog.draw( self, surface, interpol, time_sec )

        self.stage.draw( surface, interpol, time_sec )
            
    def is_done( self ):
        return self._is_done


class StageHumanCount (Component):

    def __init__( self ):
        Component.__init__( self )

        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )

        self.add_subcomponent( Label( Vec2D(200, 200), _("Number of players?"), btnFont ) )
        
        self.buttons = []
        for i in range( 2, 7 ):
            self.buttons.append( Button( Rectangle(365, 180 + i * 40, 35, 35) ) )
            self.buttons[-1].set_label( str(i), btnFont )
            self.add_subcomponent( self.buttons[-1] )

        self.guistate = GuiState()
        self.update_neighbors()

        self.player_count = None

    def tick( self, userinput, guistate ):
        self.guistate.update(userinput, self)
        Component.tick( self, userinput, self.guistate )
        
        i = 1
        for btn in self.buttons:
            if btn.went_down():
                Event.button()
                self.player_count = i+1
            i += 1

        if userinput.key.went_down( K_ESCAPE ):
            self.player_count = -1

        SingleSwitch.tick( userinput, self.guistate )

    def get_player_count( self ):
        return self.player_count

class StagePlayerConfig (Component):

    def __init__( self, game_data, player_cnt ):
        Component.__init__( self )

        self.game_data = game_data
        self.game_data.goldcars = []
        self.player_cnt = player_cnt
        self.current_player = 1

        btnFont = Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )

        self.textLabel = Label( Vec2D(250, 300), _("Player 1, press button!"), btnFont )

        self.car_sprite = resman.get("game.car1_sprite")
        self.carLabel =  Label( Vec2D(400, 240), image=self.car_sprite )
        self.anim_timer = LoopAnimationTimer( 15, 40, 12 )                

        
        self.add_subcomponent( self.textLabel )
        self.add_subcomponent( self.carLabel )

        self.forbidden_buttons = [input.Button(self.game_data.userinput.key, K_ESCAPE)]

    def tick( self, userinput, guistate ):
        Component.tick( self, userinput, guistate )

        for dev in userinput.devs_no_mouse:
            if dev.any_went_down():
                Event.playerkey()
                button = input.Button(dev, dev.went_down_buttons[0])

                if button not in self.forbidden_buttons:
                    resman.get("gui.key_good_sound").play()
                    self.forbidden_buttons.append( button )
                    
                    if self.current_player <= self.player_cnt:
                        player_data = [_("Player %d") % self.current_player, ctrl.HumanController( None, button )]
                        self.game_data.goldcars.append( player_data )

                    self.current_player += 1
                    if self.current_player <= self.player_cnt:
                        self.update_labels()
                else:
                    resman.get("gui.key_bad_sound").play()

    def update_labels( self ):
        self.textLabel.set_text( _("Player %d, press button!") % self.current_player )
        self.car_sprite = resman.get( "game.car%d_sprite" % self.current_player )
        self.carLabel.set_image( self.car_sprite )

    def is_done( self ):
        return self.current_player > self.player_cnt

    def draw( self, surface, interpol, time_sec ):
        self.car_sprite.nr = self.anim_timer.get_frame( time_sec )

        Component.draw( self, surface, interpol, time_sec )

        

class ScreenLevelSelect (Screen):

    UNLOCK, LEVELS, CONGRATS, EDIT, PLAY, MENU = range(6)

    def __init__( self, game_data ):
        Screen.__init__( self )

        self.game_data = game_data
        self._is_done = False
        
        btnFont = Font( "data/edmunds.ttf", color=(64,64,64), size=22, use_antialias = True )

        self.menu_btn = ImageButton( copy.copy(resman.get("game.lvl_left_button")), Vec2D(35, 500) )
        self.menu_btn.set_label( _("        Menu"), btnFont )
        self.play_btn = ImageButton( copy.copy(resman.get("game.lvl_right_button")), Vec2D(800-158-35,500) )
        self.play_btn.set_label( _("Play         "), btnFont )

        self.add_subcomponent( self.menu_btn )
        self.add_subcomponent( self.play_btn )

        self._init_levelpoints( self.game_data )

        if self.game_data.finished_game():
            self.state = ScreenLevelSelect.CONGRATS
            self.unlock_timer = 0
            self.fireworks = Fireworks()
        elif self.game_data.can_unlock_item():
            self.state = ScreenLevelSelect.UNLOCK
            self.unlock_timer = 0
        else:
            self.state = ScreenLevelSelect.LEVELS

        self.background = resman.get("gui.levelselect_surf")
        self.font = pygame.font.Font("data/edmunds.ttf", 20)
        self.fontL = pygame.font.Font("data/edmunds.ttf", 28)

        self.scenario = self.game_data.get_quest().create_scenario(self.game_data.skill_level.value)
        self.info = ScenarioInfo( self.scenario, self.game_data )
        self.levelpoints[ self.game_data.get_quest().progress ].set_selected()

        desc_font = Font( "data/edmunds.ttf", color=(0,0,0), size=20, use_antialias = True )

        self.description_field = TextField( Rectangle(250, 450, 300, 140), desc_font )
        self.description_field.is_enabled = False
        self.add_subcomponent( self.description_field )

        self.crate_hud = CrateHud( game_data )


        self.update_neighbors()
        self.init_active = True

    def _init_levelpoints( self, game_data, cheat = False ):
        self.lines = [[(162, 399), (127, 374), (99, 352)], [(58, 354), (49, 287), (55, 235), (64, 210), (89, 196), (123, 196)], [(156, 194), (149, 156), (133, 123), (109, 101), (81, 95), (62, 95)], [(129, 61), (160, 51), (185, 45), (218, 48), (251, 57), (278, 60)], [(319, 67), (334, 96), (348, 121), (348, 142), (342, 159), (326, 167)], [(286, 186), (289, 205), (294, 228), (312, 267)], [(324, 278), (341, 292), (367, 309), (395, 320), (422, 322), (450, 314), (484, 295), (503, 273)], [(472, 260), (497, 244), (529, 232), (552, 204), (556, 171), (532, 158)], [(472, 162), (437, 154), (406, 137), (407, 112), (418, 92), (451, 81), (494, 73), (524, 78), (701, 103), (729, 121), (739, 155), (725, 181), (702, 186), (676, 177), (650, 171), (641, 182), (640, 213), (655, 232)], [(750, 214), (733, 240), (717, 270), (692, 289), (662, 318), (641, 349), (646, 372)], [(732, 393), (696, 421), (657, 453)]]
#        self.lines = [[(98, 443), (165, 372)], [(200, 384), (281, 323), (267, 295)], [(189, 315), (105, 302), (138, 264), (222, 254)], [(257, 270), (306, 216), (262, 184)], [(202, 218), (116, 205), (103, 163), (209, 146), (281, 119)], [(322, 131), (400, 110), (435, 131), (407, 159)], [(386, 155), (379, 189), (448, 219), (457, 241)], [(484, 238), (497, 269), (472, 292), (424, 295)], [(399, 291), (390, 323), (478, 337), (565, 308)], [(575, 305), (582, 270), (601, 259), (559, 245), (565, 227)], [(584, 222), (588, 200), (554, 182)], [(535, 190), (489, 157), (526, 130), (523, 113), (566, 89), (699, 84), (751, 95), (762, 115), (739, 141), (745, 159), (678, 196), (693, 230)], [(710, 238), (694, 277)], [(682, 281), (684, 308), (744, 326), (757, 370), (737, 394)], [(706, 385), (667, 449)]]

        self.lines_length = 0.0

        for seq in self.lines:
            for i in range( 0, len(seq) - 1 ):
                a = Vec2D( seq[i][0], seq[i][1] )
                b = Vec2D( seq[i+1][0], seq[i+1][1] )

                diff = a - b

                self.lines_length += diff.length()        

        
        self.levelpoints = Radiobuttons()

        total_points = game_data.quest.get_level_count()
        config = Configuration.get_instance()
        for i in range( total_points ):
            sprite = resman.get("gui.levelpoint_sprite").clone()
            levelpoint = ImageCheckbox( sprite, self._get_point_place(i, total_points) )
            levelpoint.is_enabled = (i <= config.unlocked_level) or cheat
            self.levelpoints.append( levelpoint )

    def _get_point_place( self, i, total ):
        pos = i * self.lines_length / total

        pos_it = 0.0
        prev_pos_it = 0.0

        for seq in self.lines:
            for i in range( 0, len(seq) - 1 ):
                a = Vec2D( seq[i][0], seq[i][1] )
                b = Vec2D( seq[i+1][0], seq[i+1][1] )

                diff = b - a
                pos_it += diff.length()

                if pos_it >= pos:
                    interpol = (pos - prev_pos_it) / (pos_it - prev_pos_it)
                    diff *= interpol

                    return a + diff - Vec2D(8,8)

                prev_pos_it = pos_it

        assert False                            

    def tick( self, userinput, guistate ):
        if self.state == ScreenLevelSelect.LEVELS:
            if self.init_active:
                guistate.set_active( self.play_btn )
                self.init_active = False
            
            super(type(self), self).tick( userinput, guistate )

            self.levelpoints.tick( userinput, guistate )
            if self.levelpoints.get_selected_index() is not None and \
               self.game_data.get_quest().progress != self.levelpoints.get_selected_index():
                self.game_data.get_quest().to_level( self.levelpoints.get_selected_index() )
                self.game_data.save_single_player_progress()
                self.scenario = self.game_data.get_quest().create_scenario(self.game_data.skill_level.value)
                self.info = ScenarioInfo( self.scenario, self.game_data )

            action_button = self.game_data.goldcars[0][1].action_button

            if self.menu_btn.went_down():
                Event.button()
                self.state = ScreenLevelSelect.MENU
                self._is_done = True
            elif self.play_btn.went_down()\
                 or action_button.went_down():
                Event.button()
                self.state = ScreenLevelSelect.PLAY
                self._is_done = True
            # Cheat code for unlocking all levels
            elif userinput.key.is_down(K_F5) and userinput.key.is_down(K_F8) and userinput.key.went_down(K_PAGEDOWN):
                self._init_levelpoints(self.game_data, True)

            self.description_field.text = self.scenario.description

            SingleSwitch.tick( userinput, guistate )

        elif self.state == ScreenLevelSelect.UNLOCK:

            if self.unlock_timer == 5:
                self.crate_hud.start_unlock()
                resman.get("gui.unlock_sound").play(2)
            elif self.unlock_timer == 20*2:
                self.crate_hud.stop_unlock()
                self.game_data.unlock_item()
            elif self.unlock_timer == 20*5:
                self.state = ScreenLevelSelect.LEVELS
            
            self.crate_hud.tick()            
            self.unlock_timer += 1
            
        elif self.state == ScreenLevelSelect.CONGRATS:
            self.fireworks.tick()
            self.unlock_timer += 1

            if self.unlock_timer > 25*5 and \
               (userinput.key.any_went_down() or userinput.mouse.any_went_down()):
                self.state = ScreenLevelSelect.LEVELS
        else:
            if userinput.mouse.went_down( Mouse.LEFT ):
                self.lines[-1].append( (userinput.mouse.pos.x,
                                        userinput.mouse.pos.y) )
                print self.lines[-1][-1]
            if userinput.key.went_down( K_n ):
                print "new line"
                self.lines.append([])
            elif userinput.key.went_down( K_p ):
                print "self.lines =", self.lines


    def draw( self, surface, interpol, time_sec ):
        self.background.draw( surface, (0,0) )
        
        Screen.draw( self, surface, interpol, time_sec )
        self.levelpoints.draw( surface, interpol, time_sec )

        center = Vec2D( surface.get_width()/2, surface.get_height()/2 )
        
        if self.state == ScreenLevelSelect.LEVELS:
            self.info.draw_title( surface, time_sec, (center.x, 410) )
            self.info.draw_pickup( surface, time_sec, (center.x + 30, 600-60 ) )
            self.info.draw_opponents( surface, time_sec, (center.x - 120 + 35, 600-60+17 ) )

            # draw skill level
            txt = self.font.render( _("skill: %(name)s (%(value).0f)") % {"name":self.game_data.skill_level.name, "value":self.game_data.skill_level.value*100}, True, (255,255,255) )
            surface.blit( txt, (240, 340) )
                            
        elif self.state == ScreenLevelSelect.UNLOCK:
            y = 410

            txt = self.fontL.render( _("Unlocking item"), True, (0,0,0) )
            surface.blit( txt, (center.x - txt.get_width()/2, y) )

            self.crate_hud.draw( surface )

            # draw skill level
            txt = self.font.render( _("skill: %(name)s (%(value).0f)") % {"name":self.game_data.skill_level.name, "value":self.game_data.skill_level.value*100}, True, (255,255,255) )
            surface.blit( txt, (240, 340) )

        elif self.state == ScreenLevelSelect.CONGRATS:
            self.fireworks.draw( surface, interpol, time_sec )
##        # draw help lines
##        for seq in self.lines:
##            for i in range( 0, len(seq) - 1 ):
##                a = ( seq[i][0], seq[i][1] )
##                b = ( seq[i+1][0], seq[i+1][1] )
##            
##                pygame.draw.line( surface, (255,0,0), a, b )

            
    def is_done( self ):
        return self._is_done

    def get_state( self ):
        return self.state

class Fireworks:

    GRAVITY = Vec2D( 0, 1 )
    sprite = None

    class Spot:
        def __init__( self, color, pos, speed, damping, life_count, sub_color ):
            if color >= 0:
                self.color = color
            else:
                self.color = random.randint(0, 6)
            self.pos = pos
            self.speed = speed
            self.damping = damping
            self.life_count = life_count
            self.sub_color = sub_color

            if Fireworks.sprite is None:
                Fireworks.sprite = resman.get("gui.fireworks_sprite").clone()

        def tick( self ):
            self.speed = self.speed * self.damping + Fireworks.GRAVITY
            self.pos = self.pos + self.speed

            self.life_count -= 1

        def is_alive( self ):
            return self.life_count > 0

        def explode( self ):
            if self.sub_color is None:
                return []
            else:
                Event.fireworks_explode()
                list = []
                for i in range(0,100):
                    speed = Vec2D( random.uniform(-15, 15), random.uniform(-15, 15) )
                    if speed.length() > 0:
                        speed = speed.normalize() * random.uniform(1,15)
                    if self.sub_color >= 0:
                        color = self.sub_color
                    else:
                        color = random.randint(0,6)
                    list.append( Fireworks.Spot( color, self.pos, speed, 0.9, random.randint(5, 12), None ) )
                return list

        def draw( self, surface, interpol ):
            Fireworks.sprite.nr = self.color
            pos = self.pos + (self.speed * interpol)
            Fireworks.sprite.draw( surface, pos )

    def __init__( self ):
        self.spots = []

        self.dark_surf = gfx.Surface( (800, 600) )
        self.dark_surf.pysurf.fill( (0, 0, 0, 160) )
        self.dark_surf.pysurf.set_alpha( 160 )

        self.congrats_surf = gfx.Surface("data/gfx/congrats.png")

    def tick( self ):
        if len( self.spots ) == 0:
            Event.fireworks_start()
            for i in range(0, random.randint(1, 6) ):
                pos = Vec2D( random.randint( 200, 600 ), random.randint( 300, 500 ) )
                speed = Vec2D( random.uniform(-2, 2 ), random.uniform( -20, -30 ) )
                color = random.randint(-1, 5) 
                self.spots.append( Fireworks.Spot( color, pos, speed, 1.0, random.randint(12, 25), color ) )
        
        new_spots = []
        for spot in self.spots:
            spot.tick()

            if spot.is_alive():
                new_spots.append( spot )
            else:
                new_spots.extend( spot.explode() )

        self.spots = new_spots


    def draw( self, surface, interpol, time_sec ):
        self.dark_surf.draw( surface, (0,0) )
        self.congrats_surf.draw( surface, (70,350) )

        for spot in self.spots:
            spot.draw( surface, interpol )

class ScenarioInfo:

    def __init__( self, scenario, game_data = None ):
        self.scenario = scenario
        self.game_data = game_data
        self.font = gfx.Font("data/edmunds.ttf", 20, (0,0,0), True)
        self.title_font = gfx.Font("data/edmunds.ttf", 28, (0,0,0), True)
        
        self.init_pickup_surf()
        self.init_title_sprites()

    def init_pickup_surf( self ):
        self.pickup_surf = None
        self.pickup_y = 30
        if len(self.scenario.pickups) > 0:
            pickup = self.scenario.pickups[0]
            if pickup is pickups.Dynamite:
                self.pickup_surf = resman.get("game.dynamite_sprite").clone()
            elif pickup is Torch:
                self.pickup_surf = resman.get("game.torch_sprite").clone()
                self.pickup_y = 10
            elif pickup is Key:
                self.pickup_surf = resman.get("game.key_sprite").clone()
                self.pickup_y = 10
            elif pickup is Oiler:
                self.pickup_surf = resman.get("game.oiler_sprite").clone()
            elif pickup is Balloon:
                self.pickup_surf = resman.get("game.balloon_sprite").clone()
                self.pickup_y = 15
            elif pickup is Ghost:
                self.pickup_surf = resman.get("game.ghost_sprite").clone()                
                self.pickup_y = 0

    def init_title_sprites( self ):
        self.title_sprite_left = None
        self.title_sprite_right = None
        self.title_sprite_left_y = 0
        self.title_sprite_right_y = 0
        
        if isinstance( self.scenario, scenarios.ScenarioCoinCollect ):
            self.title_sprite_left = resman.get("game.copper_sprite").clone()
            self.title_sprite_right = resman.get("game.copper_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 25, 0, self.title_sprite_left.max_x )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, self.title_sprite_left.max_x )
            self.title_sprite_left_y = 23
            self.title_sprite_right_y = 23
        elif isinstance( self.scenario, scenarios.ScenarioHoldLamp ):
            self.title_sprite_left = resman.get("game.lamp_sprite").clone()
            self.title_sprite_right = resman.get("game.lamp_sprite").clone()
            self.left_anim_timer = None
            self.right_anim_timer = None
            self.title_sprite_left_y = 33
            self.title_sprite_right_y = 33
        elif isinstance( self.scenario, scenarios.ScenarioCutter ):
            self.title_sprite_left = resman.get("game.axe_sprite").clone()
            self.title_sprite_right = resman.get("game.gold_sprite").clone()
            self.left_anim_timer = gfx.PingPongTimer( 25, 0, 8 )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, 15 )
            self.title_sprite_left_y = 26
            self.title_sprite_right_y = 33
        elif isinstance( self.scenario, scenarios.ScenarioBlowup ):
            self.title_sprite_left = resman.get("game.dynamite_sprite").clone()
            self.title_sprite_right = resman.get("game.dynamite_sprite").clone()
            self.left_anim_timer = None
            self.right_anim_timer = None
            self.title_sprite_left_y = 35
            self.title_sprite_right_y = 35
        elif isinstance( self.scenario, scenarios.ScenarioRace ):
            self.title_sprite_left = resman.get("game.flag1_sprite").clone()
            self.title_sprite_right = resman.get("game.flag2_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 20, 0, 8 )
            self.right_anim_timer = gfx.LoopAnimationTimer( 20, 0, 8 )
            self.title_sprite_left_y = 7
            self.title_sprite_right_y = 7
        elif isinstance( self.scenario, scenarios.ScenarioCollectRocks ):
            self.title_sprite_left = resman.get("game.rock_sprite").clone()
            self.title_sprite_right = resman.get("game.rock_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 25, 0, 15 )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, 15 )
            self.title_sprite_left_y = 39
            self.title_sprite_right_y = 39
        elif isinstance( self.scenario, scenarios.ScenarioDiamondCollect ):
            self.title_sprite_left = resman.get("game.diamond_sprite").clone()
            self.title_sprite_right = resman.get("game.diamond_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 25, 0, 4 )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, 4 )
            self.title_sprite_left_y = 27
            self.title_sprite_right_y = 27
        elif isinstance( self.scenario, scenarios.ScenarioCollectAll ):
            self.title_sprite_left = resman.get("game.copper_sprite").clone()
            self.title_sprite_right = resman.get("game.diamond_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 25, 0, self.title_sprite_left.max_x )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, 4 )
            self.title_sprite_left_y = 23
            self.title_sprite_right_y = 27
        elif isinstance( self.scenario, scenarios.ScenarioPacman ):
            self.title_sprite_left = resman.get("game.copper_sprite").clone()
            self.title_sprite_right = resman.get("game.copper_sprite").clone()
            self.left_anim_timer = gfx.LoopAnimationTimer( 25, 0, self.title_sprite_left.max_x )
            self.right_anim_timer = gfx.LoopAnimationTimer( 25, 0, self.title_sprite_left.max_x )
            self.title_sprite_left_y = 23
            self.title_sprite_right_y = 23

    def draw_pickup( self, surface, time_sec, pos ):
        if self.pickup_surf is not None:
            self.font.draw( _("pickup:"), surface, pos )
            self.pickup_surf.draw( surface, Vec2D(pos[0], pos[1] ) + Vec2D(90, self.pickup_y) )

    def draw_title( self, surface, time_sec, pos ):
        self.title_font.draw( self.scenario.title, surface, pos, gfx.Font.CENTER )

        width = self.title_font.get_width( self.scenario.title )
        left_pos = Vec2D( pos[0] - width/2 - 25, pos[1] + self.title_sprite_left_y  )
        right_pos = Vec2D( pos[0] + width/2 + 25, pos[1] + self.title_sprite_right_y  )

        if self.title_sprite_left is not None:
            if self.left_anim_timer is not None:
                self.title_sprite_left.nr = self.left_anim_timer.get_frame( time_sec )
            self.title_sprite_left.draw( surface, left_pos )
            
        if self.title_sprite_right is not None:
            if self.right_anim_timer is not None:
                self.title_sprite_right.nr = self.right_anim_timer.get_frame( time_sec )
            self.title_sprite_right.draw( surface, right_pos )

    def draw_opponents( self, surface, time_sec, pos ):
        opponent_count = len(self.game_data.get_quest().get_opponent_iqs())

        pos = Vec2D(pos[0], pos[1]) - Vec2D(35, 17) * ((opponent_count-1)/2)
        
        for i in range(0, opponent_count):
            offset = Vec2D(i*35, i*17)
            sprite = copy.copy(resman.get("game.car%d_sprite" % (i+2)))
            sprite.nr = 0
            sprite.draw( surface, pos + offset )

class CrateHud:
    """Crates at the bottom of the window"""
    
    def __init__( self, game_data ):
        self.game_data = game_data
        
        self.crate_sprite = resman.get("game.crate_sprite")
        self.crate_label = resman.get("game.crate_label_surf")

        self.unlock_timer = 0
        self.teaser_timer = -20
        self.teaser_cnt = -1
        self.teaser_dir = 1

    def tick( self ):
        if self.unlock_timer > 0:
            self.unlock_timer += 1

            self.teaser_timer = -200
            self.teaser_cnt = -1
            self.teaser_dir = 1
        else:
            self.teaser_timer += 1
            if self.teaser_timer > 3:
                if self.teaser_cnt == -1 and self.teaser_dir == -1:
                    self.teaser_timer = -100
                    self.teaser_dir = 1
                else:
                    self.teaser_timer = 0
                    self.teaser_cnt += self.teaser_dir
                    if self.teaser_cnt == 10:
                        self.teaser_dir = -1


    def start_unlock( self ):
        self.unlock_timer = 1

    def stop_unlock( self ):
        self.unlock_timer = 0

    def draw( self, surface ):
        for i in range(0,11):
            if (i < self.game_data.unlocked_item_count) \
                or \
               (i == self.game_data.unlocked_item_count and \
               (self.unlock_timer % 4 > 1)) \
                or \
               (i == self.teaser_cnt):
                self.crate_sprite.nr = i+1
            else:
                self.crate_sprite.nr = 0

            # Quick Hack because dynamite and diamond are swapped
            if self.crate_sprite.nr == 1:
                self.crate_sprite.nr = 2
            elif self.crate_sprite.nr == 2:
                self.crate_sprite.nr = 1
            
            self.crate_sprite.draw( surface, Vec2D(15 + i*73, 600-66) )

        self.crate_label.draw( surface, Vec2D(0, 600-100) )

        font = Font( "data/edmunds.ttf", color=(0,0,0), size=20, use_antialias = True )
        font.draw(_("Secret Items:"), surface, (18, 600-97))



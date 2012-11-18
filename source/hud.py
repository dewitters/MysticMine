#!/usr/bin/env python

import pygame.font
import copy

from koon.geo import Vec2D, Rectangle
import koon.geo as geo
from koon.res import resman
import koon.gui as gui
import koon.gfx as gfx
from koon.input import Keyboard, Mouse
import control as ctrl
import settings
import menu
from world import *
import pickups
import event

class Hud:
    def __init__( self, scenario, ground_control, game_data ):
        self.font = gfx.Font("data/edmunds.ttf", 20, use_antialias = True)
        self.font_white = gfx.Font("data/edmunds.ttf", 20, (255,255,255), use_antialias = True)
        self.font_score = gfx.Font("data/edmunds.ttf", 18, (255,255,255), use_antialias = True)
        self.font_watch = gfx.Font("data/edmunds.ttf", 18, (0,0,0), use_antialias = True)
        self.scenario = scenario
        self.ground_control = ground_control
        self.game_data = game_data
        self.dialog = None

        self.guistate = gui.GuiState()

        btnFont = gfx.Font( "data/edmunds.ttf", color=(0,0,0), size=19, use_antialias = True )        
        self.menu_btn = gui.ImageButton( copy.copy(resman.get("game.hud_menu_button_sprite")), Vec2D(5, 257) )
        self.menu_btn.set_label( _("Menu"), btnFont )

        self.last_clock_ring = None

    def game_tick( self, indev ):
        if self.dialog is not None:
            self.dialog.do_tick( indev )

            if isinstance( self.dialog, TipDlg ) and \
               self.dialog.all_is_ready():
                self.dialog = IntroDlg( self.scenario, self.ground_control )

        self.menu_btn.tick(indev, self.guistate)

        timeout = self.scenario.get_timeout()
        if timeout is not None and timeout <= 10:
            if timeout != self.last_clock_ring:
                if timeout > 0:
                    event.Event.clock()
                else:
                    event.Event.clock_ring()
                self.last_clock_ring = timeout

            
    def draw( self, frame ):
        resman.get("game.hud_score_surf").draw( frame.surface, Vec2D(0,0) )
        resman.get("game.hud_watch_surf").draw( frame.surface, Vec2D(5,290) )
        
        y = 7

        for goldcars in self.scenario.playfield.get_goldcar_ranking():
            for goldcar in goldcars:
                sprite = copy.copy(resman.get("game.car%d_sprite" % (goldcar.nr+1)))
                sprite.nr = 20 * goldcar.amount

                sprite.draw( frame.surface, Vec2D(24, y + 30) )

                self.font_score.draw( "%d" % (goldcar.score), frame.surface,
                                      (110, y + 4), align = gfx.Font.RIGHT )
                
                y += 35
                
        timeout = self.scenario.get_timeout()
        if timeout is not None:
            time_string = "%01d:%02d" % (timeout/60, timeout%60)
            time_x = 0
            for char in time_string:
                self.font_watch.draw( char, frame.surface, (49 + time_x, 383), align=gfx.Font.CENTER )
                time_x += 10

        if self.dialog is not None:
            self.dialog.draw( frame )

        if not isinstance( self.dialog, IntroDlg ):
            self.font_white.draw( self.scenario.mission_txt, frame.surface, (130, 5 ) )

        self.menu_btn.draw( frame.surface, frame.interpol, frame.time_sec )

    def start_intro_screen( self ):
        self.dialog = self._get_tip_dialog()
        if self.dialog is None:
            self.dialog = IntroDlg( self.scenario, self.ground_control )

    def start_end_screen( self ):
        self.dialog = EndDlg( self.scenario, self.ground_control )

    def start_total_screen( self ):
        self.dialog = TotalDlg( self.scenario, self.ground_control, self.game_data )

    def start_win_screen( self ):
        self.dialog = WinDlg( self.scenario, self.ground_control, self.game_data )

    def start_lose_screen( self ):
        self.dialog = LoseDlg( self.scenario, self.ground_control, self.game_data )

    def end_info( self ):
        self.dialog = None

    def is_ready( self ):
        if isinstance( self.dialog, TipDlg ):
            return False
        if self.dialog is not None:
            return self.dialog.all_is_ready()
        else:
            return True
                    
    def _get_tip_dialog( self ):
        if self.game_data.is_single_player():
            if self.game_data.quest.progress == 0:
                return TrackTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 3:
                return DiamondTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 6:
                return PassDiamondTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 8:
                return DynamiteTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 22:
                return LampTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 33:
                return BalloonTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 45:
                return CutterTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 58:
                return FlagTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 72:
                return OilTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 88:
                return RockTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 101:
                return TorchTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 115:
                return GhostTipDlg( self.scenario, self.ground_control )
            elif self.game_data.quest.progress == 132:
                return KeyTipDlg( self.scenario, self.ground_control )
        return None

class BaseDlg (gui.Dialog):
    def __init__( self, scenario, ground_control ):
        gui.Dialog.__init__( self, Rectangle(140, 80, 800-200, 600-200 ) ) 
        self.background_image = resman.get("gui.paperdialog_surf")
        
        self.scenario = scenario
        self.ground_control = ground_control

        self.font = gfx.Font("data/edmunds.ttf", 20, use_antialias = True)
        self.large_font = gfx.Font( "data/edmunds.ttf", 28, use_antialias = True )
        self.small_font = gfx.Font( "data/edmunds.ttf", 16, use_antialias = True )

        self.guistate = gui.GuiState()
        
    def do_tick( self, indev ):
        self.guistate.update( indev, self )

        gui.Dialog.tick( self, indev, self.guistate )

    def draw( self, frame ):
        gui.Dialog.draw( self, frame.surface, frame.interpol, frame.time_sec )
        
    
class MultiDlg (BaseDlg):
    def __init__( self, scenario, ground_control ):
        BaseDlg.__init__( self, scenario, ground_control )
        
        self.no_input_timeout = 25*1

        self.all_ready = False
        self.readys = None

        self.anim_timer = gfx.LoopAnimationTimer( 15, 0, 12 )


    def do_tick( self, indev ):
        BaseDlg.do_tick( self, indev )
        
        if self.no_input_timeout <= 0:
            if self.readys is None:
                self.readys = [ isinstance( gc, ctrl.AiController ) for gc in self.ground_control.controllers ]

            i = 0
            for controller in self.ground_control.controllers:
                goldcar_rect = Rectangle( self.get_goldcar_x( i ) - 30, 
                    400, 60, 80)

                if (isinstance(controller, ctrl.HumanController) and \
                   controller.action_button.went_down()) \
                   or \
                   (indev.mouse.went_down(Mouse.LEFT) and \
                   goldcar_rect.contains( indev.mouse.pos ) ):
                    self.readys[i] = True
                i += 1

            if not False in self.readys:        
                self.all_ready = True
        else:
            self.no_input_timeout -= 1

    def get_goldcar_x( self, place ):
        left_x = 400 - 180
        right_x = 400 + 180
        if len(self.scenario.playfield.goldcars) == 1:
            return left_x + (right_x-left_x) * place
        else:
            return left_x + (right_x-left_x) * place / (len(self.scenario.playfield.goldcars)-1)

    def draw( self, frame ):
        BaseDlg.draw( self, frame )
        
        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = 365
        
        if self.no_input_timeout <= 0:
            self.font.draw( _("Press your button or click on the car"), frame.surface, (center.x, y+15), gfx.Font.CENTER )

            y = 415
            
            place = 0
            for controller in self.ground_control.controllers:
                goldcar = controller.goldcar

                x = self.get_goldcar_x( place )

                if isinstance(controller, ctrl.HumanController):
                    button_text = "< %s >" % controller.action_button.get_name()
                    self.small_font.draw( button_text, frame.surface, (x, y + 30), gfx.Font.CENTER )

                sprite = copy.copy(resman.get("game.car%d_sprite" % (goldcar.nr+1)))

                if self.readys is not None:
                    if self.readys[place]:
                        self.small_font.draw( _("Ready!"), frame.surface, (x, y+50), gfx.Font.CENTER )
                        sprite.nr = 60
                    else:
                        self.small_font.draw( _("waiting..."), frame.surface, (x, y+50), gfx.Font.CENTER )
                        sprite.nr = self.anim_timer.get_frame( frame.time_sec )

                sprite.draw( frame.surface, Vec2D(x, y + 26) )
                    
                place += 1

    def all_is_ready( self ):
        return self.all_ready
    

class TipDlg (BaseDlg):
    def __init__( self, scenario, ground_control ):
        BaseDlg.__init__( self, scenario, ground_control )

        self.play_btn  = gui.Button( Rectangle(500,450,100,40) )
        self.play_btn.set_label( _("OK"), self.large_font )
        self.add_subcomponent( self.play_btn )

        self.description_field = gui.TextField( Rectangle(200, 150, 400, 140), self.font )
        self.description_field.is_enabled = False
        self.add_subcomponent( self.description_field )

        self.update_neighbors()

        self.is_ready = False

    def do_tick( self, indev ):
        BaseDlg.do_tick( self, indev )

        if self.play_btn.went_down():
            self.is_ready = True

    def all_is_ready( self ):
        return self.is_ready

    def draw( self, frame ):
        BaseDlg.draw( self, frame )

        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 200

        self.large_font.draw( _("Info: "),
                              frame.surface, (center.x, y), gfx.Font.CENTER )


class TrackTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Switch the track with spacebar. You can also click on the track with your mouse to switch it.")

        self.playfield = Playfield()

        x = 2
        y = 7
        self.playfield.level = Level()        
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y,0), Tile.Type.FLAT, Trail.Type.EW ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y-1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y-2,0), Tile.Type.FLAT ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+1,y), 500)
        self.carpos.reverse_progress()
        self.playfield.goldcars = [GoldCar(copy.copy(self.carpos), 0)]

        self.timer = 0;

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()
        self.playfield.goldcars[0].pos = copy.copy(self.carpos)
        self.playfield.goldcars[0].select_next_switch()

        self.timer += 1
        if self.timer > 15:
            self.playfield.goldcars[0].keydown()
            self.timer = 0

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.interpol = 0.0
        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True
        
class KeyTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("A key switches all tracks on the playfield.")

        self.playfield = Playfield()

        x = 2
        y = 7
        self.playfield.level = Level()        
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y,0), Tile.Type.FLAT, Trail.Type.EW ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+2,0), Tile.Type.FLAT, Trail.Type.EW ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+2,0), Tile.Type.FLAT, Trail.Type.EW ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y-1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y-2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y-2,0), Tile.Type.FLAT, Trail.Type.EW ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y-2,0), Tile.Type.FLAT, Trail.Type.EW ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+1,y), 500)
        self.carpos.reverse_progress()
        self.playfield.goldcars = [GoldCar(copy.copy(self.carpos), 0)]
        self.playfield.goldcars[0].collectible = pickups.Key()
        self.playfield.goldcars[0].collectible.container = self.playfield.goldcars[0]

        self.timer = 0;

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()
        self.playfield.goldcars[0].pos = copy.copy(self.carpos)
        self.playfield.goldcars[0].select_next_switch()

        self.timer += 1
        if self.timer > 15:
            self.playfield.goldcars[0].keydown()
            self.timer = 0

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.interpol = 0.0
        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class PassPickupTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.playfield = Playfield()

        self.playfield.level = Level()        
        self._fill_level()

    def _fill_level( self ):
        x = 2
        y = 7
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y-1,0), Tile.Type.EAST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y,0), Tile.Type.EAST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+6,y-1,0), Tile.Type.WEST_SLOPE_TOP ) )

        pos = [TrailPosition(self.playfield.level.get_tile(x+1,y), 500),
               TrailPosition(self.playfield.level.get_tile(x+3,y), 500)]
        self.playfield.goldcars = [GoldCar(pos[i], i) for i in range(0,2)]

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class DynamiteTipDlg (PassPickupTipDlg):

    def __init__( self, scenario, ground_control ):
        PassPickupTipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Pass the dynamite by bumping into other car.")

        self.dynamite = pickups.Dynamite()
        self.playfield.goldcars[0].add_pickup(self.dynamite)

    def do_tick( self, indev ):
        PassPickupTipDlg.do_tick( self, indev )

        self.dynamite.life = 0.9   

class LampTipDlg (PassPickupTipDlg):

    def __init__( self, scenario, ground_control ):
        PassPickupTipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Pass the lamp by bumping into other car.")
        
        self.playfield.goldcars[0].add_pickup(pickups.Lamp())
        

class DiamondTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Bring the diamond to a tunnel.")

        self.playfield = Playfield()

        x = 3
        y = 5
        self.playfield.level = Level()        
        self.playfield.level.set_tile( Enterance( Vec3D(x+3,y+0,0) ))
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Enterance( Vec3D(x+3,y+3,0) ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+1,y), 500)
        self.carpos.reverse_progress()
        self.playfield.goldcars = [GoldCar(copy.copy(self.carpos), 0)]

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        diamond_cnt = self.playfield.get_pickup_count( pickups.Diamond )
        
        if diamond_cnt < 1:
            self.playfield.spawn_pickup( pickups.Diamond() )


    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

        resman.get("gui.enterdlg_surf").draw(frame.surface, geo.Vec2D(0,0))

class PassDiamondTipDlg (PassPickupTipDlg):

    def __init__( self, scenario, ground_control ):
        PassPickupTipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Pass the diamond by bumping into other car.")

        self.diamond = pickups.Diamond()
        self.playfield.goldcars[0].add_pickup(self.diamond)

    def do_tick( self, indev ):
        PassPickupTipDlg.do_tick( self, indev )


class BalloonTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("With a balloon you can only go up.")

        self.playfield = Playfield()

        x = 0
        y = 5
        self.playfield.level = Level()
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+0,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+6,y-1,0), Tile.Type.WEST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+7,y-1,0), Tile.Type.FLAT ) )

        self.playfield.level.set_tile( Tile( Vec3D(x+5,y+1,0), Tile.Type.EAST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+5,y+2,0), Tile.Type.EAST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+6,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+7,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+8,y+2,0), Tile.Type.FLAT ) )

        self.playfield.level.set_tile( Tile( Vec3D(x+7,y+0,0), Tile.Type.NORTH_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+8,y+0,0), Tile.Type.NORTH_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+8,y+1,0), Tile.Type.FLAT ) )


        self.carpos = TrailPosition(self.playfield.level.get_tile(x+8,y+1), 500)
        self.playfield.goldcars = [GoldCar(self.carpos, 0)]

        self.timer = 0

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        self.timer += 1

        if self.timer == 25*3:
            balloon_cnt = self.playfield.get_pickup_count( pickups.Balloon )        
            
            if balloon_cnt < 1:
                self.playfield.spawn_pickup( pickups.Balloon() )
        elif self.timer == 25*9:
            self.playfield.goldcars[0].collectible = None
            self.timer = 0
            
    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class CutterTipDlg (PassPickupTipDlg):

    def __init__( self, scenario, ground_control ):
        PassPickupTipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Only the car with axe can cut gold.")
        
        self.playfield.goldcars[0].add_pickup(pickups.Axe())

    def _fill_level( self ):
        x = 2
        y = 7
        self.playfield.level.set_tile( Tile( Vec3D(x+6,y-3,0), Tile.Type.WEST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y-2,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y-2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y-2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y-2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y-2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y-1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+6,y-1,0), Tile.Type.WEST_SLOPE_TOP ) )

        pos = [TrailPosition(self.playfield.level.get_tile(x+0,y-2), 500),
               TrailPosition(self.playfield.level.get_tile(x+0,y), 500)]
        self.playfield.goldcars = [GoldCar(pos[i], i) for i in range(0,2)]
        self.playfield.goldcars[0].pos.reverse_progress()
        
    def do_tick( self, indev ):
        PassPickupTipDlg.do_tick( self, indev )

        gold_cnt = self.playfield.get_pickup_count( pickups.GoldBlock )        
        
        if gold_cnt < 1:
            self.playfield.spawn_pickup( pickups.GoldBlock() )

class FlagTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Only your own flag can be collected.")

        self.playfield = Playfield()

        x = 3
        y = 5
        self.playfield.level = Level()        
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+0,0), Tile.Type.FLAT ) )

        pos = [TrailPosition(self.playfield.level.get_tile(x+0,y+0), 500),
               TrailPosition(self.playfield.level.get_tile(x+3,y+3), 500)]
        self.playfield.goldcars = [GoldCar(pos[i], i) for i in range(0,2)]
        self.playfield.goldcars[0].pos.reverse_progress()

        self.tiles = [None for i in range(0, 10)]

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        i = 0
        for gc in self.playfield.goldcars:
            while self.tiles[i] is None:
                self.tiles[i] = self.playfield.spawn_pickup( pickups.Flag(gc) )

            # Reset when flag is gone
            if self.tiles[i].pickup is None:
                self.tiles[i] = None
                
            i += 1


    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class OilTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("Go up slopes with oil.")

        self.playfield = Playfield()

        x = 3
        y = 4
        self.playfield.level = Level()
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+4,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+1,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+0,0), Tile.Type.WEST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+4,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+3,0), Tile.Type.WEST_SLOPE_TOP ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+0,y+1), 500)
        self.carpos.reverse_progress()
        self.playfield.goldcars = [GoldCar(self.carpos, 0)]

        self.timer = 0

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        self.timer += 1

        if self.timer == 25*3:
            oil_cnt = self.playfield.get_pickup_count( pickups.Oiler )        
            
            if oil_cnt < 1:
                x = 3
                y = 4 + 3
                tile = self.playfield.level.get_tile(x, y)
                tile.pickup = pickups.Oiler()
                tile.pickup.container = tile
                
        elif self.timer == 25*11:
            self.playfield.goldcars[0].modifier = None
            self.timer = 0        

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class RockTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("You can't pickup anything when you have a rock. Lose the rock in a tunnel.")

        self.playfield = Playfield()

        x = 3
        y = 5
        self.playfield.level = Level()        
        self.playfield.level.set_tile( Enterance( Vec3D(x+3,y+0,0) ))
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Enterance( Vec3D(x+3,y+3,0) ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+1,y), 500)
        self.carpos.reverse_progress()
        self.playfield.goldcars = [GoldCar(copy.copy(self.carpos), 0)]

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        rock_cnt = self.playfield.get_pickup_count( pickups.RockBlock )
        coin_cnt = self.playfield.get_pickup_count( pickups.CopperCoin )
        
        if rock_cnt < 1:
            self.playfield.spawn_pickup( pickups.RockBlock() )
        if coin_cnt < 2:
            self.playfield.spawn_pickup( pickups.CopperCoin() )

        x = 3
        y = 5
        if isinstance(self.playfield.level.get_tile(x+2, y+0).pickup, pickups.CopperCoin):
            self.playfield.level.get_tile(x+2, y+0).pickup = None


    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

        resman.get("gui.enterdlg_surf").draw(frame.surface, geo.Vec2D(0,0))

class TorchTipDlg (TipDlg):

    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("A Torch moves every car to a different location")

        self.playfield = Playfield()
        self.playfield.level = Level()        
        self._fill_level()

        self.playfield.goldcars = []

        tile = None
        while tile is None:
            tile = self.playfield.spawn_pickup( pickups.Torch() )

    def _fill_level( self ):
        x = 2
        y = 7
        self.playfield.level.set_tile( Tile( Vec3D(x+2,y,0), Tile.Type.FLAT ) )

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True

class GhostTipDlg (TipDlg):
    def __init__( self, scenario, ground_control ):
        TipDlg.__init__( self, scenario, ground_control )

        self.description_field.text = _("A ghost makes you go up slopes and move through other cars.")

        self.playfield = Playfield()

        x = 3
        y = 4
        self.playfield.level = Level()
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+4,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+0,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+1,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+0,0), Tile.Type.WEST_SLOPE_TOP ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+0,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+1,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+2,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+4,y+3,0), Tile.Type.FLAT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+1,y+4,0), Tile.Type.WEST_SLOPE_BOT ) )
        self.playfield.level.set_tile( Tile( Vec3D(x+3,y+3,0), Tile.Type.WEST_SLOPE_TOP ) )

        self.carpos = TrailPosition(self.playfield.level.get_tile(x+0,y+1), 500)
        self.carpos.reverse_progress()
        self.carpos2 = TrailPosition(self.playfield.level.get_tile(x+4,y+1), 500)
        self.playfield.goldcars = [GoldCar(self.carpos, 0),
                                   GoldCar(self.carpos2, 1)]

        self.timer = 0

    def do_tick( self, indev ):
        TipDlg.do_tick( self, indev )

        self.playfield.game_tick()

        self.timer += 1

        if self.timer == 25*3:
            ghost_cnt = self.playfield.get_pickup_count( pickups.Ghost )        
            
            if ghost_cnt < 1:
                x = 3
                y = 4 + 3
                tile = self.playfield.level.get_tile(x, y)
                tile.pickup = pickups.Ghost()
                tile.pickup.container = tile
                
        elif self.timer == 25*11:
            self.playfield.goldcars[0].modifier = None
            self.playfield.goldcars[1].modifier = None
            self.timer = 0        

    def draw( self, frame ):
        TipDlg.draw( self, frame )

        frame.optimize_speed = False
        frame.draw( self.playfield )
        frame.optimize_speed = True
        

class IntroDlg( MultiDlg ):
    def __init__( self, scenario, ground_control ):
        MultiDlg.__init__( self, scenario, ground_control )

        self.info = menu.ScenarioInfo( scenario )

    def draw( self, frame ):
        MultiDlg.draw( self, frame )

        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        #self.large_font.draw( "Game: %s" % self.scenario.title,
        #                      frame.surface, (center.x, y), gfx.Font.CENTER )

        self.info.draw_title( frame.surface, frame.time_sec, (center.x, y) )
        self.info.draw_pickup( frame.surface, frame.time_sec, (center.x + 50, 240 ) )
        

        y += 50 
    
        self.font.draw( self.scenario.description, frame.surface,
                        (center.x, y), gfx.Font.CENTER )

    
class EndDlg( MultiDlg ):
    def __init__( self, scenario, ground_control ):
        MultiDlg.__init__( self, scenario, ground_control )

    def draw( self, frame ):
        MultiDlg.draw( self, frame )

        #winner = None
        #for goldcar in self.playfield.goldcars:
        #    if winner is None or winner.score < goldcar.score:
        #        winner = goldcar
        
        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        self.large_font.draw( _("Game Ended!"), frame.surface,
                               (center.x, y), gfx.Font.CENTER )

        y += 32
        self.font.draw( _("Ranking"), frame.surface, (center.x - 150, y) )

        ranking = self.scenario.playfield.get_goldcar_ranking()

        place = 1
        y -= 5
        for goldcars in ranking:            
            y += 32

            self.font.draw( "%d." % place, frame.surface,
                            (center.x - 170, y), gfx.Font.RIGHT )

            goldcar_x = center.x - 140
            for goldcar in goldcars:
                sprite = copy.copy(resman.get("game.car%d_sprite" % (goldcar.nr+1)))
                sprite.nr = 20 * goldcar.amount
                sprite.draw( frame.surface, Vec2D(goldcar_x, y + 26) )
                goldcar_x += 40

                place += 1

            self.font.draw( "%d" % goldcars[0].score, frame.surface,
                              (center.x + 100, y), gfx.Font.RIGHT )

class TotalDlg( MultiDlg ):
    def __init__( self, scenario, ground_control, game_data ):
        MultiDlg.__init__( self, scenario, ground_control )
        self.game_data = game_data

    def draw( self, frame ):
        MultiDlg.draw( self, frame )

        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        self.large_font.draw( _("All Games Total"), frame.surface,
                               (center.x, y), gfx.Font.CENTER )

        y += 32
        self.font.draw( _("Ranking"), frame.surface, (center.x - 150, y) )

        ranking = self.game_data.get_total_ranking()

        place = 1
        y -= 5
        amount = 3
        for goldcars in ranking:            
            y += 32

            self.font.draw( "%d." % place, frame.surface,
                            (center.x - 170, y), gfx.Font.RIGHT )

            goldcar_x = center.x - 140
            for goldcar in goldcars:
                sprite = copy.copy(resman.get("game.car%d_sprite" % (goldcar.nr+1)))
                sprite.nr = 20 * amount
                sprite.draw( frame.surface, Vec2D(goldcar_x, y + 26) )
                goldcar_x += 40

                place += 1

            amount = max( [0, amount - 1] )
            self.font.draw( "%d" % goldcars[0].score, frame.surface,
                              (center.x + 100, y), gfx.Font.RIGHT )

class SingleDlg( MultiDlg ):
    def __init__( self, scenario, ground_control, game_data ):
        MultiDlg.__init__( self, scenario, ground_control )
        self.game_data = game_data

        self.font_red = gfx.Font("data/edmunds.ttf", 20, (200,0,0), use_antialias = True)
        self.font_tiny = gfx.Font("data/edmunds.ttf", 15, (0,0,0), use_antialias = True)
        self.font_tiny_red = gfx.Font("data/edmunds.ttf", 15, (200,0,0), use_antialias = True)
        self.font_tiny_white = gfx.Font("data/edmunds.ttf", 15, (255,255,255), use_antialias = True)

        self.skill_value = self.game_data.skill_level.old_value
    
    def do_tick( self, indev ):
        MultiDlg.do_tick( self, indev )

        if self.skill_value < self.game_data.skill_level.value:
            self.skill_value += 0.001
        if self.skill_value > self.game_data.skill_level.value:
            self.skill_value -= 0.001

    def draw( self, frame ):
        MultiDlg.draw( self, frame )
        
        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        skill = settings.SkillLevel(self.game_data.quest.get_skill(self.scenario))

        self.font_tiny.draw( _("Played level as:"), frame.surface, (center.x-180, y + 70) )
        self.font.draw( "%s" % skill.name, frame.surface, (center.x-140, y + 90) )

        self.font_tiny.draw( _("Your current skill level:"), frame.surface, (center.x-180, y + 140) )
        self.font_red.draw( "%s" % self.game_data.skill_level.name, frame.surface, (center.x-140, y + 160) )

        self.draw_skill_bar( frame, center.x + 50, y + 70 )

    def draw_skill_bar( self, frame, x, y ):
        resman.get("game.skill_bar_surf").draw( frame.surface, Vec2D(x+10,y+85) )

        MIN_Y = y
        MAX_Y = y + 7 * 21 + 12
        pointer_y = geo.lin_ipol( self.skill_value,
                                  MAX_Y + 7, MIN_Y + 17, 0.3, 1.0 )
        pointer_y = max( min( pointer_y, MAX_Y ), MIN_Y )
        
#        pointer_y = MAX_Y

        resman.get("game.skill_pointer_surf").draw( frame.surface, Vec2D(x+10, pointer_y) )
        self.font_tiny_white.draw("%d" % int(self.skill_value * 100), frame.surface, (x+13, pointer_y+2),
                                  align=gfx.Font.CENTER, valign=gfx.Font.MIDDLE )
        
        for skill_name in settings.SkillLevel.NAMES:
            if skill_name == self.game_data.skill_level.name:
                self.font_tiny_red.draw( skill_name, frame.surface, (x+40, y) )
            else:
                self.font_tiny.draw( skill_name, frame.surface, (x+40, y) )
            y += 21


class WinDlg( SingleDlg ):
    def __init__( self, scenario, ground_control, game_data ):
        SingleDlg.__init__( self, scenario, ground_control, game_data )

    def draw( self, frame ):
        SingleDlg.draw( self, frame )
        
        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        self.large_font.draw( _("Nice job!"), frame.surface, (center.x, y), gfx.Font.CENTER )                

class LoseDlg( SingleDlg ):
    def __init__( self, scenario, ground_control, game_data ):
        SingleDlg.__init__( self, scenario, ground_control, game_data )

    def draw( self, frame ):
        SingleDlg.draw( self, frame )
        
        center = Vec2D( frame.surface.get_width()/2, frame.surface.get_height()/2 )

        y = center.y - 180

        self.large_font.draw( _("Game Over!"), frame.surface, (center.x, y), gfx.Font.CENTER )

class IngameMenu (gui.Dialog):
    def __init__( self, is_single_player, game_data ):
        super(IngameMenu, self).__init__( Rectangle(140, 80, 800-400, 600-200 ) )
        self.background_image = resman.get("gui.paperdialog_surf")
        self._is_done = False
        self.game_data = game_data

        btnFont = gfx.Font( "data/edmunds.ttf", color=(0,0,0), size=32, use_antialias = True )

        BUTTON_X = 300
        BUTTON_Y = 100
        H = 75

        self.continue_btn = gui.ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(BUTTON_X, BUTTON_Y) )
        self.continue_btn.set_label( _("Continue"), btnFont )

        self.skip_btn  = gui.ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 1*H) )
        self.skip_btn.set_label( _("Skip Level"), btnFont )
        self.options_btn  = gui.ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 2*H) )
        self.options_btn.set_label( _("Options"), btnFont )
        self.menu_btn  = gui.ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 3*H) )
        self.menu_btn.set_label( _("To Menu"), btnFont )
        self.quit_btn  = gui.ImageButton( copy.copy(resman.get("game.button02_sprite")), Vec2D(BUTTON_X, BUTTON_Y + 4*H) )
        self.quit_btn.set_label( _("Quit"), btnFont )

        self.add_subcomponent( self.continue_btn )
        if not is_single_player:
            self.add_subcomponent( self.skip_btn )
        self.add_subcomponent( self.options_btn )
        self.add_subcomponent( self.menu_btn )
        self.add_subcomponent( self.quit_btn )

        self.update_neighbors()
        
        self.options_dialog = None

        self.to_menu = False
        self.should_quit = False
        self.to_next_level = False

    def tick( self, userinput, guistate ):
        if self.options_dialog is None:
            super(IngameMenu, self).tick( userinput, guistate )
            if self.continue_btn.went_down():
                self._is_done = True
            elif self.skip_btn.went_down():
                self.to_next_level = True
                self._is_done = True
            elif self.menu_btn.went_down():
                self.to_menu = True
                self._is_done = True
            elif self.quit_btn.went_down():
                self.should_quit = True
                self._is_done = True
            elif self.options_btn.went_down():
                self.options_dialog = menu.OptionsDialog(self.game_data)
                self.add_subcomponent( self.options_dialog )
                self.is_enabled = False

            menu.SingleSwitch.tick( userinput, self.guistate )
        else:
            self.options_dialog.tick( userinput, guistate )

            if self.options_dialog.is_done():
                self.remove_subcomponent( self.options_dialog )
                self.options_dialog = None
                self.is_enabled = True


    def is_done( self ):
        return self._is_done

    

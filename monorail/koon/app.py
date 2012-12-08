
import sys
import gc

import pygame
from pygame.locals import *

from input import *
import snd

TICKS_PER_SECOND = 25
GAMETICKS = 1000 / TICKS_PER_SECOND

def set_game_speed( slowdown ):
    global TICKS_PER_SECOND
    global GAMETICKS

    TICKS_PER_SECOND = int( 25 * slowdown )
    GAMETICKS = 1000 / TICKS_PER_SECOND

class Game:

    def __init__( self, name, configuration ):
        self.config = configuration
        self.name = name

    def init_pygame( self ):
        snd.pre_init()

        # Init the display
        pygame.init()

        self.userinput = UserInput()

        if not self.config.is_fullscreen:
            pygame.display.set_mode( self.config.resolution )
        else:
            pygame.display.set_mode( self.config.resolution, pygame.FULLSCREEN )
        pygame.display.set_caption( self.name )

        # Init the input
        pygame.mouse.set_visible( False )
        pygame.event.set_grab( False )

        snd.init()

    def deinit_pygame( self ):
        snd.deinit()
        pygame.quit()

    def before_gameloop( self ):
        pass

    def after_gameloop( self ):
        pass

    def run( self ):
        try:
            self.init_pygame()

            self.before_gameloop()

            self.fps = 0
            frame_count = 0

            next_game_tick = pygame.time.get_ticks()
            next_half_second = pygame.time.get_ticks()

            # main loop
            self.game_is_done = False
            while not self.game_is_done:
                # events
                self.handle_events()

                # game tick
                loop_count = 0
                while pygame.time.get_ticks() > next_game_tick and loop_count < 4:
                    x, y = pygame.mouse.get_pos()
                    self.userinput.mouse.feed_pos( Vec2D(x, y) )

                    self.do_tick( self.userinput )
                    self.userinput.update()
                    next_game_tick += GAMETICKS
                    loop_count += 1

##                    gc.collect()

                if loop_count >= 4: # don't overdo the ticks
                    next_game_tick = pygame.time.get_ticks()

                # render
                time_sec = pygame.time.get_ticks() * 0.001
                interpol = 1 - ((next_game_tick - pygame.time.get_ticks()) / float(GAMETICKS))
                self.render(pygame.display.get_surface(), interpol, time_sec )
                pygame.display.flip()

                frame_count += 1
                if pygame.time.get_ticks() > next_half_second:
                    self.fps = 2 * frame_count
                    frame_count = 0
                    next_half_second += 500

            self.after_gameloop()

            self.deinit_pygame()

        except:
            self.deinit_pygame()
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def handle_events( self ):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.game_is_done = True
            elif event.type == KEYDOWN:
                self.userinput.key.feed_down( event.key )
                self.userinput.key.feed_char( event.unicode )
            elif event.type == KEYUP:
                self.userinput.key.feed_up( event.key )
            elif event.type == MOUSEBUTTONDOWN:
                self.userinput.mouse.feed_down( event.button )
                self.state.mouse_down( event.button )
            elif event.type == MOUSEBUTTONUP:
                self.userinput.mouse.feed_up( event.button )
            elif event.type == JOYBUTTONDOWN:
                self.userinput.joys[event.joy].feed_down( event.button )
            elif event.type == JOYBUTTONUP:
                self.userinput.joys[event.joy].feed_up( event.button )

    def draw_fps( self, surface ):
        font = pygame.font.Font( None, 20 )
        render_text = font.render( str(self.fps), 0, (255,255,255) )
        surface.blit( render_text, (10,10) )


#!/usr/bin/env python

from datetime import datetime
import time
import traceback
import sys
import os
import random
import struct
import shutil

import pygame
from pygame.locals import *

from koon.geo import Vec2D
import monorail
from settings import Configuration

ALL_KEYS = [
    K_BACKSPACE, #   \b      backspace
    K_TAB, #         \t      tab
    K_CLEAR, #               clear
    K_RETURN, #      \r      return
    K_PAUSE, #               pause
##    K_ESCAPE, #      ^[      escape
    K_SPACE, #               space
    K_EXCLAIM , #    !       exclaim
    K_QUOTEDBL, #    "       quotedbl
    K_HASH, #        #       hash
    K_DOLLAR, #      $       dollar
    K_AMPERSAND, #   &       ampersand
    K_QUOTE, #               quote
    K_LEFTPAREN, #   (       left parenthesis
    K_RIGHTPAREN, #  )       right parenthesis
    K_ASTERISK, #    *       asterisk
    K_PLUS, #        +       plus sign
    K_COMMA, #       ,       comma
    K_MINUS, #       -       minus sign
    K_PERIOD, #      .       period
    K_SLASH, #       /       forward slash
##    K_0, #           0       0
    K_1, #           1       1
    K_2, #           2       2
    K_3, #           3       3
    K_4, #           4       4
    K_5, #           5       5
    K_6, #           6       6
    K_7, #           7       7
    K_8, #           8       8
    K_9 , #          9       9
    K_COLON, #       :       colon
    K_SEMICOLON, #   ;       semicolon
    K_LESS, #        <       less-than sign
    K_EQUALS, #      =       equals sign
    K_GREATER, #     >       greater-than sign
    K_QUESTION, #    ?       question mark
    K_AT, #          @       at
    K_LEFTBRACKET, # [       left bracket
    K_BACKSLASH, #   \       backslash
    K_RIGHTBRACKET, # ]      right bracket
    K_CARET, #       ^       caret
    K_UNDERSCORE, #  _       underscore
    K_BACKQUOTE, #   `       grave
    K_a, #           a       a
    K_b, #           b       b
    K_c, #           c       c
    K_d, #           d       d
##    K_e, #           e       e
    K_f, #           f       f
    K_g, #           g       g
    K_h, #           h       h
    K_i, #           i       i
    K_j, #           j       j
    K_k, #           k       k
    K_l, #           l       l
    K_m, #           m       m
    K_n, #           n       n
    K_o, #           o       o
    K_p, #           p       p
    K_q, #           q       q
    K_r, #           r       r
    K_s, #           s       s
    K_t, #           t       t
    K_u, #           u       u
    K_v, #           v       v
    K_w, #           w       w
    K_x, #           x       x
    K_y, #           y       y
    K_z, #           z       z
    K_DELETE, #              delete
    K_KP0, #                 keypad 0
    K_KP1, #                 keypad 1
    K_KP2, #                 keypad 2
    K_KP3, #                 keypad 3
    K_KP4, #                 keypad 4
    K_KP5, #                 keypad 5
    K_KP6, #                 keypad 6
    K_KP7, #                 keypad 7
    K_KP8, #                 keypad 8
    K_KP9, #                 keypad 9
    K_KP_PERIOD, #   .       keypad period
    K_KP_DIVIDE, #   /       keypad divide
    K_KP_MULTIPLY, # *       keypad multiply
    K_KP_MINUS, #    -       keypad minus
    K_KP_PLUS, #     +       keypad plus
    K_KP_ENTER, #    \r      keypad enter
    K_KP_EQUALS, #   =       keypad equals
    K_UP, #                  up arrow
    K_DOWN, #                down arrow
    K_RIGHT, #               right arrow
    K_LEFT, #                left arrow
    K_INSERT, #              insert
    K_HOME, #                home
    K_END, #                 end
    K_PAGEUP, #              page up
    K_PAGEDOWN, #            page down
##    K_F1, #                  F1
    K_F2, #                  F2
    K_F3, #                  F3
    K_F4, #                  F4
    K_F5, #                  F5
    K_F6, #                  F6
    K_F7, #                  F7
    K_F8, #                  F8
    K_F9, #                  F9
    K_F10, #                 F10
    K_F11, #                 F11
    K_F12, #                 F12
    K_F13, #                 F13
    K_F14, #                 F14
    K_F15, #                 F15
    K_NUMLOCK, #             numlock
    K_CAPSLOCK, #            capslock
    K_SCROLLOCK, #           scrollock
    K_RSHIFT, #              right shift
    K_LSHIFT, #              left shift
    K_RCTRL, #               right ctrl
    K_LCTRL, #               left ctrl
    K_RALT, #                right alt
    K_LALT, #                left alt
    K_RMETA, #               right meta
    K_LMETA, #               left meta
    K_LSUPER, #              left windows key
    K_RSUPER, #              right windows key
    K_MODE, #                mode shift
    K_HELP, #                help
    K_PRINT, #               print screen
    K_SYSREQ, #              sysrq
    K_BREAK, #               break
    K_MENU, #                menu
    K_POWER, #               power
    K_EURO #                euro
]

TICKS_PER_SECOND = 25
GAMETICKS = 1000 / TICKS_PER_SECOND

class Monkey (monorail.Monorail):
    """A fuzzy Tester of Monorail
    """

    def __init__( self, config, replay_file = None ):
        monorail.Monorail.__init__( self, config )
        self.user_exit = False

        if replay_file is None:
            self.replay_filename = "monkeyTemp"
            self.replay_file = open("monkeyTemp", "wb")
            self.record = True
        else:
            self.replay_filename = replay_file
            self.replay_file = open(replay_file, "rb")
            self.record = False

        seed = self.random(0, sys.maxint )
        print seed
        random.seed( seed )

    def random( self, lower, upper ):
        if self.record:
            rand = random.randint(lower, upper)
            self.replay_file.write(struct.pack("i", rand))
            return rand
        else:
            rand = random.randint(lower, upper) # needed to keep seed
            try:
                data = struct.unpack("i", self.replay_file.read( struct.calcsize("i") ) )
                return data[0]
            except:
                print "Not failed this time!!!!!! Oh YEAH BABY !!!!!"
                self.game_is_done = True
                return rand

    def handle_events( self ):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.game_is_done = True
                self.user_exit = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.game_is_done = True
                self.user_exit = True

        # move mouse
        self.userinput.mouse.feed_pos( Vec2D( self.random(0, 800-1),
                                              self.random(0, 600-1) ) )

        # maybe release mouse presses
        down_buttons = self.userinput.mouse.down_buttons
        while self.random( 0, 1 ) == 0 and len(down_buttons) > 0:
            self.userinput.mouse.feed_up(
                down_buttons[ self.random(0, len(down_buttons)-1) ] )

        # generate mouse presses
        while self.random( 0, 1 ) == 0:
            key = self.random(0, 5)
            self.userinput.mouse.feed_down( key )

        # maybe release key presses
        down_buttons = self.userinput.key.down_buttons
        while self.random( 0, 1 ) == 0 and len(down_buttons) > 0:
            self.userinput.key.feed_up(
                down_buttons[ self.random(0, len(down_buttons)-1) ] )

        # feed random keys
        while self.random( 0, 10 ) <> 0:
            key = ALL_KEYS[ self.random( 0, len(ALL_KEYS)-1 ) ]
            self.userinput.key.feed_down( key )

        # sometimes escape key
        if self.random( 0, 2**20 ) == 0:
            key = K_ESCAPE
            self.userinput.key.feed_down( key )


    def run( self, timeout = None ):
        try:
            self.init_pygame()

            self.before_gameloop()

            self.fps = 0
            frame_count = 0

            next_game_tick = pygame.time.get_ticks()
            next_half_second = pygame.time.get_ticks()
            if timeout is not None:
                end_game_tick = pygame.time.get_ticks() + timeout * 1000

            # main loop
            self.game_is_done = False
            while not self.game_is_done:
                # events
                self.handle_events()

                # game tick
                loop_count = 0
                while loop_count < 1:
                    self.do_tick( self.userinput )
                    self.userinput.update()
                    next_game_tick += GAMETICKS
                    loop_count += 1

                # render
                time_sec = pygame.time.get_ticks() * 0.001
                interpol = 1 - ((next_game_tick - pygame.time.get_ticks()) / GAMETICKS)
                self.render(pygame.display.get_surface(), interpol, time_sec )
                pygame.display.flip()

                frame_count += 1
                if pygame.time.get_ticks() > next_half_second:
                    self.fps = 2 * frame_count
                    frame_count = 0
                    next_half_second += 500

                if timeout is not None and \
                                pygame.time.get_ticks() > end_game_tick:
                    self.game_is_done = True

            self.after_gameloop()

            self.deinit_pygame()

            self.replay_file.close()

            if self.record or not self.user_exit:
                os.remove(self.replay_filename)


        except Exception, ex:
            print "exceptje"
            self.deinit_pygame()
            self.replay_file.close()
            if self.record:
                shutil.move("monkeyTemp", self.create_failed())
            raise

    def create_failed( self ):
        i = 0
        while True:
            os.listdir(os.getcwd())
            f = "monkeyFailed%03d" % i
            if not f in os.listdir(os.getcwd()):
                return f

            i += 1



class MonkeyMaster:

    def run( self ):
        config = Configuration.get_instance()
        monkey = Monkey( config )

        while not monkey.user_exit:
            print "starting monkey at", datetime.today()
            monkey = Monkey( config )

            try:
                monkey.run( 60 * 5 )
                print "stopped monkey at", datetime.today()
            except Exception, ex:
                info = sys.exc_info()
                traceback.print_exception(info[0], info[1], info[2])
                time.sleep(3)

            print

if __name__ == '__main__':
    try:
        if "run" in sys.argv[1:]:
            monkeyMaster = MonkeyMaster()
            monkeyMaster.run()
        else:
            replay_file = None
            for f in os.listdir(os.getcwd()):
                if f.startswith("monkeyFailed"):
                    replay_file = f
                    break

            if replay_file is not None:
                monkey = Monkey( Configuration.get_instance(), replay_file )
                monkey.run()
            else:
                print "No failed files!"
    except Exception, ex:
        print "megaexcept!!!!!!"


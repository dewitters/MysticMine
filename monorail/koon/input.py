""" Contains keyboard, mouse, joysticks, etc...

"""

from geo import Vec2D
import pygame

class ButtonLogger:
    def __init__( self ):
        self.went_down_buttons = []
        self.went_up_buttons = []
        self.down_buttons = []

    def feed_down( self, key ):
        self.went_down_buttons.append( key )
        self.down_buttons.append( key )

    def feed_up( self, key ):
        self.went_up_buttons.append( key )
        try:
            self.down_buttons.remove( key )
        except: pass

    def update( self ):
        self.went_down_buttons = []
        self.went_up_buttons = []

    def went_down( self, key ):
        return key in self.went_down_buttons

    def went_up( self, key ):
        return key in self.went_up_buttons

    def any_went_down( self, keys = None ):
        if keys is not None:
            for k in keys:
                if self.went_down( k ):
                    return True
            return False
        else:
            return len( self.went_down_buttons ) > 0

    def any_went_up( self, keys = None ):
        if keys is not None:
            for k in keys:
                if self.went_up( k ):
                    return True
            return False
        else:
            return len( self.went_up_buttons ) > 0

    def is_down( self, key ):
        return key in self.down_buttons

    def any_is_down( self, keys = None ):
        if keys is not None:
            for k in keys:
                if self.is_down( k ):
                    return True
            return False
        else:
            return len( self.down_buttons ) > 0

class Keyboard (ButtonLogger):

    def __init__( self ):
        ButtonLogger.__init__( self )
        self._char_buffer = ""

    def feed_char( self, char ):
        self._char_buffer += char

    def get_chars( self ):
        return self._char_buffer

    def update( self ):
        ButtonLogger.update( self )
        self._char_buffer = ""

    def get_name( self, key ):
        return pygame.key.name( key )

class Mouse (ButtonLogger):
    """The mouse interface

    public members:
    - pos: the current Vec2D position of the mouse
    """
    UNKNOWN, LEFT, RIGHT, MIDDLE, SCROLLUP, SCROLLDOWN = range( 6 )

    def __init__( self ):
        ButtonLogger.__init__( self )
        self.pos = None
        self._prev_pos = None

    def feed_pos( self, pos ):
        self._prev_pos = self.pos
        self.pos = pos

    def has_moved( self ):
        return self._prev_pos is not None and \
               self._prev_pos <> self.pos

class Joystick (ButtonLogger):
    def get_name( self, key ):
        return "joy " + str(key)

class UserInput:
    def __init__( self ):
        self.key = Keyboard()
        self.mouse = Mouse()
        self.joys = []
        for i in range( 0, pygame.joystick.get_count() ):
            joy = pygame.joystick.Joystick( i )
            joy.init()
            self.joys.append( Joystick() )

        self.devs_no_mouse = [ self.key ]
        self.devs_no_mouse.extend( self.joys )

    def update( self ):
        self.key.update()
        self.mouse.update()
        for joy in self.joys:
            joy.update()

    def any_went_up( self ):
        for dev in self.devs_no_mouse:
            if dev.any_went_up():
                return True

        return False

    def any_went_down( self ):
        for dev in self.devs_no_mouse:
            if dev.any_went_down():
                return True

        return False

class Button (object):
    def __init__( self, device, button ):
        self.dev = device
        self.button = button

    def __eq__( self, other ):
        return self.dev == other.dev and self.button == other.button

    def __ne__( self, other ):
        return not (self == other)

    def __hash__( self ):
        return hash( self.dev ) ^ hash( self.button )

    def get_name( self ):
        return self.dev.get_name( self.button )

    def went_down( self ):
        return self.dev.went_down( self.button )


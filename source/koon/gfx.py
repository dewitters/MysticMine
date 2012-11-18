#!/usr/bin/env python

import copy
from Numeric import array

import pygame

from geo import Vec2D, Rectangle

class Surface:
    def __init__( self, param ):
        """Return a new Surface instance.

        Parameter param can be a filename, a pygame.Surface or a
        (width, height) tuple.
        
        """
        assert param is not None

        # param is filename
        if isinstance( param, str ):
            self.pysurf = pygame.image.load( param ).convert_alpha()

        # param is pygame.Surface
        elif isinstance( param, pygame.Surface ):
            self.pysurf = param

        # param is (width, height)
        elif isinstance( param, tuple ) and len( param ) == 2:
            self.pysurf = pygame.Surface( param )

    def draw( self, surface, pos, rect = None ):
        """Draw this surface onto surface at pos

        pos is a Vec2D or (x,y) tuple
        """
        if isinstance( pos, tuple ):
            pos = Vec2D( pos[0], pos[1] )
        
        if isinstance( surface, pygame.Surface ):
            if rect is not None:
                surface.blit( self.pysurf, pos.get_tuple(), rect )
            else:
                surface.blit( self.pysurf, pos.get_tuple() )
        else:
            if rect is not None:
                surface.pysurf.blit( self.pysurf, pos.get_tuple(), rect )
            else:
                surface.pysurf.blit( self.pysurf, pos.get_tuple() )

    def get_width( self ):
        return self.pysurf.get_width()

    def get_height( self ):
        return self.pysurf.get_height()

    def get_size( self ):
        return self.pysurf.get_size()

    def set_alpha( self, alpha ):
        self.pysurf.set_alpha( alpha )

    def get_blended( self, alpha ):
        assert alpha >= 0.0 and alpha <= 1.0
        result = Surface((self.get_width(), self.get_height()))
        result.pysurf = self.pysurf.copy()
        
        a = pygame.surfarray.pixels_alpha(result.pysurf)
        b = a * array(alpha)
        a[:] = b.astype('b')

        return result


class SubSurf:
    """Part of a surface that can be drawn

    Members:
    - surface: the image (gfx.Surface)
    - rect: the part of the image (rectangle)
    - offset: the Vec2D offset when drawn
    """
    def __init__( self, surface, rect = None, offset = Vec2D(0,0) ):
        self.surface = surface
        self.rect = rect
        self.offset = offset

    def draw( self, surface, pos ):
        """Draw this onto surface at pos

        pos is a Vec2D
        """
        self.surface.draw( surface, pos - self.offset, self.rect )

class Sprite:
    """Contains surface frames
    """
    def __init__( self ):
        pass

class SpriteSub (Sprite):
    """Contains surface frames of subsurfs
    """
    def draw( self, surface, pos ):
        self.frames = []

    def get_frame( self, nr ):
        return subsurf

    def load( self, filename ):
        pass

    def save( self, filename ):
        pass

class SpriteFilm (Sprite):
    """Contains surface frames of equal size

    Members:
    
    surface: the sprite image
    nr: sprite nr to draw
    center: center of the sprite (Vec2D)
    width: the width of a sprite
    height: the height of a sprite
    """
    def __init__( self, surface = None ):
        self.nr = 0
        self.surface = surface

    def set_dimension( self, width, height ):
        self.width = width
        self.height = height
        self.max_x = self.surface.get_width() / width

    def set_div( self, x_sprites, y_sprites ):
        self.width = self.surface.get_width() / x_sprites
        self.height = self.surface.get_height() / y_sprites
        self.max_x = x_sprites
        self.center = Vec2D(self.width, self.height) / 2

    def draw( self, surface, pos, rect = None ):
        """Draw the sprite on the surface at pos

        pos is a Vec2D
        """
        sp_x = (self.nr % self.max_x) * self.width
        sp_y = (self.nr / self.max_x) * self.height

        sprite_rect = [sp_x, sp_y, self.width, self.height]

        if rect is not None:
            r = copy.copy(rect)
            r.pos = r.pos + Vec2D(sp_x, sp_y)
            sprite_rect = (Rectangle.from_tuple(sprite_rect) & r).get_tuple()

        self.surface.draw( surface, pos - self.center, sprite_rect)

    def get_size( self ):
        return (self.width, self.height)

    def clone( self ):
        cl = copy.copy( self )
        return cl

class Font:
    LEFT, RIGHT, CENTER = range(3)
    TOP, BOTTOM, MIDDLE = range(3)
    
    def __init__( self, filename = None, size = 16, color = (0,0,0), \
                  use_antialias = False ):
        if filename is None:
            filename = "freesansbold.ttf"
        self.filename = filename
        self.color = color
        self._use_antialias = use_antialias
        self.pygame_font = pygame.font.Font( filename, size )

    def set_size( self, size ):
        self.pygame_font = pygame.font.Font( self.filename, size )

    def set_color( self, color ):
        self.color = color

    def set_antialias( self, use_antialias ):
        self._use_antialias = use_antialias

    def use_antialias( self ):
        return self._use_antialias

    def draw( self, text, surface, (x, y), align = LEFT, valign = TOP ):
        textsurf = self.pygame_font.render( text, self._use_antialias,
                                            self.color )
        textsurf = Surface( textsurf )

        if   align == Font.TOP:     pass
        elif align == Font.CENTER:  x -= textsurf.get_width() / 2
        else:                       x -= textsurf.get_width()

        if valign == Font.TOP:      pass
        elif valign == Font.MIDDLE: y -= textsurf.get_height() / 2
        else:                       y -= textsurf.get_height()

        textsurf.draw( surface, (x, y) )

    def _get_height( self ):
        return self.pygame_font.get_height()
    height = property( _get_height )

    def get_width( self, text ):
        return self.pygame_font.size( text )[0]

class Timer:

    def __init__( self, hertz ):
        self.timeskip = 1.0 / hertz

    def start( self, time_sec ):
        self.next_tick = time_sec

    def do_tick( self, time_sec ):
        # initialize when not done already
        if not hasattr(self, 'next_tick'):
            self.start( time_sec - self.timeskip )
        
        if self.next_tick < time_sec:
            self.next_tick += self.timeskip
            return True
        else:
            return False

class LoopAnimationTimer:

    def __init__( self, fps, firstframe, maxframes ):
        self.fps = fps
        self.firstframe = firstframe
        self.maxframes = maxframes

        self.set_frame( 0, firstframe )

    def set_frame( self, time, frame ):
        self.starttime = time
        self.startframe = frame

    def get_frame( self, time ):
        frame = int( (time - self.starttime) * self.fps )

        frame = (frame + self.startframe) % self.maxframes
        
        return frame + self.firstframe
        
        
class PingPongTimer:

    def __init__( self, fps, firstframe, maxframes ):
        self.fps = fps
        self.firstframe = firstframe
        self.maxframes = maxframes

        self.set_frame( 0, firstframe )

    def set_frame( self, time, frame ):
        self.starttime = time
        self.startframe = frame

    def get_frame( self, time ):
        frame = int( (time - self.starttime) * self.fps )

        frame = (frame + self.startframe) % (self.maxframes*2)

        if frame >= self.maxframes:
            frame = self.maxframes*2 - frame
        
        return frame + self.firstframe
        
        

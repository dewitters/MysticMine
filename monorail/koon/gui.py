
import pygame
import pygame.draw as draw
from pygame.locals import *

from geo import Vec2D, Rectangle
from gfx import *
from input import *


class GuiState (object):
    """Keeps track of the gui state

    GuiState, and not the components, handles everything todo with active
    components.

    The active state is the selected state when using the keyboard, or
    the mouse-over state when using a pointing device. It is basically the
    component that has the current focus.
    """

    def __init__( self ):
        self.active = None # the active component that receives input

    def set_active( self, component ):
        self.active = component

    def get_active( self ):
        return self.active

    def update( self, userinput, component ):
        self._update_active( userinput, component )

    def activate_next( self ):
        if self.active.next_neighbor is not None:
            self.set_active( self.active.next_neighbor )
            while not self.active.is_enabled: self.set_active( self.active.next_neighbor )

    def activate_prev( self ):
        if self.active.prev_neighbor is not None:
            self.set_active( self.active.prev_neighbor )
            while not self.active.is_enabled: self.set_active( self.active.prev_neighbor )

    def _update_active( self, userinput, component ):
        interactives = GuiState._get_interactive_components( component )

        if self.active is not None and not self.active.has_input_lock():
            if userinput.key.went_down( K_UP ):
                self.activate_prev()
            if userinput.key.went_down( K_DOWN ):
                self.activate_next()

        if userinput.mouse.has_moved() and \
           (self.active is None or not self.active.has_input_lock()):
            for comp in interactives:
                if comp.place.contains( userinput.mouse.pos ) and comp.is_enabled:
                    self.set_active( comp )

        if userinput.mouse.went_down( Mouse.LEFT ):
            if self.active is not None and self.active.has_input_lock():
                self.active.lock_input( False )
            for comp in interactives:
                if comp.place.contains( userinput.mouse.pos ) and comp.is_enabled:
                    self.set_active( comp )

        if self.active is None or self.active not in interactives or not self.active.is_enabled:
            if len(interactives) > 0:
                self.set_active( interactives[0] )


    @staticmethod
    def _get_interactive_components( component ):
        interactives = []

        if isinstance( component, InteractiveComponent ) and \
           component.delegate_active is None:
            interactives.append( component )

        for sub in component.subs:
            interactives.extend( GuiState._get_interactive_components( sub ) )

        return interactives

class Component (object):
    """The base class of all gui components"""

    def __init__( self ):
        """Creates new instance"""
        self.subs = []
        self.is_enabled = True
        self.is_visible = True
        self.place = Rectangle( 0, 0, 0, 0 )

    def tick( self, userinput, guistate  ):
        """Calls tick for all sub components"""
        for sub in self.subs:
            sub.tick( userinput, guistate )

    def draw( self, surface, interpol=0.0, time_sec=0.0 ):
        """Calls draw for all sub components"""
        if self.is_visible:
            for sub in self.subs:
                sub.draw( surface, interpol, time_sec )

    def add_subcomponent( self, subcomponent ):
        self.subs.append( subcomponent )

    def remove_subcomponent( self, subcomponent ):
        self.subs.remove( subcomponent )

    def update_neighbors( self ):
        """Update the neighbors for key navigation"""

        comps = GuiState._get_interactive_components( self )

        if len(comps) > 2:
            for i in range(0, len(comps)-1):
                comps[i].next_neighbor = comps[i+1]

            for i in range(1, len(comps)):
                comps[i].prev_neighbor = comps[i-1]

            comps[0].prev_neighbor = comps[-1]
            comps[-1].next_neighbor = comps[0]

class InteractiveComponent (Component):
    """Component that can interact with user input

    Members:
    place: Rectangle with the place
    """

    def __init__( self, place ):
        Component.__init__( self )
        self.place = place
        self._has_input_lock = False

        self.next_neighbor = None
        self.prev_neighbor = None

        self.delegate_active = None

    def has_input_lock( self ):
        """Return true when this component has a hard activation (receives input)"""
        return self._has_input_lock;

    def lock_input( self, has_input_lock ):
        self._has_input_lock = has_input_lock


class Screen (Component):
    def draw( self, surface, interpol=0.0, time_sec=0.0 ):
        super(Screen, self).draw( surface, interpol, time_sec )

    def tick( self, userinput, guistate  ):
        super(Screen, self).tick( userinput, guistate )
        guistate.update( userinput, self )

class Dialog (Component):

    def __init__( self, place ):
        super(Dialog, self).__init__()

        self.place = place
        self.background_image = None

        # we have our own guistate
        self.guistate = GuiState()

    def tick( self, userinput, guistate  ):
        super(Dialog, self).tick( userinput, self.guistate )
        self.guistate.update( userinput, self )

    def draw( self, surface, interpol=0.0, time_sec=0.0 ):

        if self.background_image is not None:
            self.background_image.draw( surface, self.place.pos )
        else:
            surface.fill( (50, 50, 50), self.place.get_tuple() )

        super(Dialog, self).draw( surface, interpol, time_sec )


class ImageDialog (Dialog):
    def __init__( self ):
        self.pos = Vec2D( 0, 0 )
        pass

    def set_surf( self, surface ):
        self.surf = surface

        xc = surface.get_width()
        xa = xc / 3
        xb = xc * 2 / 3
        yc = surface.get_height()
        ya = yc / 3
        yb = yc * 2 / 3

        self.top_left  = Rect(  0,  0, xa, ya )
        self.top_cen   = Rect( xa,  0, xb-xa, ya )
        self.top_right = Rect( xb,  0, xc-xb, ya )

        self.mid_left  = Rect(  0, ya, xa, yb-ya )
        self.mid_cen   = Rect( xa, ya, xb-xa, yb-ya )
        self.mid_right = Rect( xb, ya, xc-xb, yb-ya )

        self.bot_left  = Rect(  0, yb, xa, yc-yb )
        self.bot_cen   = Rect( xa, yb, xb-xa, yc-yb )
        self.bot_right = Rect( xb, yb, xc-xb, yc-yb )

        self.set_block_size( 1, 1 )

    def set_block_size( self, x, y ):
        self.block_size = Vec2D( x, y )

    def get_width( self ):
        return self.top_left.width + self.top_cen.width * self.block_size.x + self.top_right.width

    def get_height( self ):
        return self.top_left.height + self.mid_left.height * self.block_size.y + self.bot_left.height

    def get_size( self ):
        return Vec2D( self.get_width(), self.get_height() )

    def draw( self, backbuffer, interpol=0.0, time_sec=0.0 ):
        x = self.pos.x
        y = self.pos.y
        self.surf.draw( backbuffer, Vec2D(x, y), self.top_left )
        x += self.top_left.width
        for i in range( self.block_size.x ):
            self.surf.draw( backbuffer, Vec2D(x, y), self.top_cen )
            x += self.top_cen.width
        self.surf.draw( backbuffer, Vec2D(x, y), self.top_right )

        y += self.top_left.height

        for j in range( self.block_size.y ):
            x = self.pos.x
            self.surf.draw( backbuffer, Vec2D(x, y), self.mid_left )
            x += self.mid_left.width
            for i in range( self.block_size.x ):
                self.surf.draw( backbuffer, Vec2D(x, y), self.mid_cen )
                x += self.mid_cen.width
            self.surf.draw( backbuffer, Vec2D(x, y), self.mid_right )

            y += self.mid_left.height

        x = self.pos.x
        self.surf.draw( backbuffer, Vec2D(x, y), self.bot_left )
        x += self.bot_left.width
        for i in range( self.block_size.x ):
            self.surf.draw( backbuffer, Vec2D(x, y), self.bot_cen )
            x += self.bot_cen.width
        self.surf.draw( backbuffer, Vec2D(x, y), self.bot_right )

class Button (InteractiveComponent):
    SELECT_KEYS = [K_SPACE, K_RETURN, K_KP_ENTER]

    def __init__( self, place = Rectangle(0,0,0,0) ):
        InteractiveComponent.__init__( self, place )
        self.label = None
        self._went_down = False
        self.is_down = False
        self.active = False

    def tick( self, userinput, guistate ):
        Component.tick( self, userinput, guistate )


        self._went_down = False

        if self.is_enabled:
            # Check if mouse went down on button
            if userinput.mouse.went_down( Mouse.LEFT ) and \
                       self.place.contains( userinput.mouse.pos ):
                self._went_down = True

            # Check if key went down on this button
            if guistate is not None and \
               guistate.get_active() == self and \
               userinput.key.any_went_down( Button.SELECT_KEYS ):
                self._went_down = True

            self.is_down = False
            if userinput.mouse.is_down( Mouse.LEFT ) and \
                       self.place.contains( userinput.mouse.pos ):
                self.is_down = True

            if guistate is not None and \
               guistate.get_active() == self and \
               userinput.key.any_is_down( Button.SELECT_KEYS ):
                self.is_down = True

        self.active = (guistate is not None and guistate.get_active() == self)


    def draw( self, surface, interpol, time_sec ):
        Component.draw( self, surface, interpol, time_sec )

        if self.active:
            draw.rect( surface, (194,194,194), self.place.get_tuple(), 3 )
        else:
            draw.rect( surface, (0,0,0), self.place.get_tuple(), 3 )

        if self.label is not None:
            pos = self.place.pos + self.place.size / 2
            pos.y += 3
            self.font.draw( self.label, surface, pos.get_tuple(), Font.CENTER, Font.MIDDLE )

    def went_down( self ):
        return self._went_down

    def set_label( self, label, font ):
        self.label = label
        self.font = font

class Checkbox (Button):
    """Used for both checkbox and radiobutton"""

    def __init__( self, place = Rectangle(0,0,0,0), selected = False ):
        Button.__init__( self, place )

        self.selected = selected

    def is_selected( self ):
        return self.selected

    def set_selected( self, selected = True ):
        self.selected = selected

    def tick( self, userinput, guistate ):
        Button.tick( self, userinput, guistate )

        if self.is_enabled and self.went_down():
            self.selected = not self.selected

    def draw( self, surface, interpol, time_sec ):
        Component.draw( self, surface, interpol, time_sec )

        if self.selected:
            surface.fill( (255,255,255), self.place.get_tuple() )
        else:
            draw.rect( surface, (255,255,255), self.place.get_tuple(), 2 )

        if self.label is not None:
            pos = self.place.pos + self.place.size / 2
            if self.selected:
                self.selected_font.draw( self.label, surface, pos.get_tuple(), Font.CENTER, Font.MIDDLE )
            else:
                self.font.draw( self.label, surface, pos.get_tuple(), Font.CENTER, Font.MIDDLE )

    def set_label( self, label, font ):
        self.label = label
        self.font = font
        self.selected_font = copy.copy(font)
        self.selected_font.set_color( (255-font.color[0],
                                       255-font.color[1],
                                       255-font.color[2] ) )


class Radiobuttons (Component):

    def __init__( self ):
        Component.__init__( self )
        self.checkboxes = []
        self.selected_index = None

    def tick( self, userinput, guistate  ):
        Component.tick( self, userinput, guistate )

        # deselect previous selected
        index = 0
        for checkbox in self.checkboxes:
            if checkbox.is_selected() and checkbox is not self.get_selected():
                if self.get_selected() is not None:
                    self.get_selected().set_selected( False )
                self.select( index )

            index += 1

        # make sure current is selected
        if self.get_selected_index() is not None:
            self.checkboxes[ self.get_selected_index() ].set_selected( True )

    def append( self, checkbox ):
        self.checkboxes.append( checkbox )
        self.add_subcomponent( checkbox )

    def __len__( self ):
        return len( self.checkboxes )

    def __getitem__( self, index ):
        return self.checkboxes[ index ]

    def get_selected( self ):
        if self.selected_index is not None:
            return self.checkboxes[ self.selected_index ]
        else:
            return None

    def select( self, index ):
        self.selected_index = index

    def get_selected_index( self ):
        return self.selected_index

class ImageButton (Button):
    def __init__( self, sprite, pos = Vec2D(0,0) ):
        """Create a new instance

        sprite is a gfx.Sprite with 3 frames: normal, active, disabled
        """
        Button.__init__(self, Rectangle(pos.x,# - sprite.center.x,
                                        pos.y,# - sprite.center.y,
                                        sprite.width, sprite.height))

        self.sprite = sprite
        self.sprite.nr = 0
        self.label = None

    def set_pos( self, pos ):
        self.place.pos = pos #- self.sprite.center
    pos = property( lambda self: self.place.pos, set_pos )

    def tick( self, userinput, guistate ):
        Button.tick( self, userinput, guistate )

        self.sprite.nr = 0
        if not self.is_enabled:
            self.sprite.nr = 2
        elif guistate is not None and self == guistate.get_active():
            self.sprite.nr = 1

    def draw( self, surface, interpol, time_sec ):
        Component.draw( self, surface, interpol, time_sec )

        self.sprite.draw( surface, self.place.pos )# + self.sprite.center)

        if self.label is not None:
            pos = self.place.pos + self.place.size / 2
            self.font.draw( self.label, surface, pos.get_tuple(), Font.CENTER, Font.MIDDLE )

    def set_label( self, label, font ):
        self.label = label
        self.font = font

class ImageCheckbox (Checkbox):
    def __init__( self, sprite, pos = Vec2D(0,0) ):
        """Create a new instance

        sprite is a gfx.Sprite with 5 frames:
        normal, selected, normal-active, selected-active, disabled
        """
        Checkbox.__init__(self, Rectangle(pos.x, pos.y, sprite.width, sprite.height))

        self.sprite = sprite
        self.sprite.nr = 1
        self.animTimer = PingPongTimer( 20, 1, 3 )

    def tick( self, userinput, guistate ):
        Checkbox.tick( self, userinput, guistate )

        if self.is_selected():
            self.sprite.nr = 3
        else:
            self.sprite.nr = 1

        if self == guistate.get_active():
            self.sprite.nr = 4

        if not self.is_enabled:
            self.sprite.nr = 0

    def draw( self, surface, interpol, time_sec ):
        if self.is_selected():
            self.sprite.nr = self.animTimer.get_frame( time_sec )
        Component.draw( self, surface, interpol, time_sec )

        self.sprite.draw( surface, self.place.pos )

class Slider (InteractiveComponent):
    def __init__( self, place = Rectangle(0,0,0,0) ):
        InteractiveComponent.__init__( self, place )
        self._value = 0.5
        self._old_value = self._value
        self._is_sliding = False

    def tick( self, userinput, guistate ):
        Component.tick( self, userinput, guistate )

        # Check if mouse is down on slider
        if userinput.mouse.is_down( Mouse.LEFT ) and \
               (self._is_sliding or self.place.contains( userinput.mouse.pos )):
            self._value = float(userinput.mouse.pos.x - self.place.pos.x) \
                          / (self.place.get_right() - self.place.pos.x )
            self._value = min(1.0, max(0.0, self._value))
            self._is_sliding = True

        self._went_up = False
        if userinput.mouse.went_up( Mouse.LEFT ) and self._is_sliding:
            self._went_up = True
            self._is_sliding = False

    def draw( self, surface, interpol, time_sec ):
        Component.draw( self, surface, interpol, time_sec )

        draw.rect( surface, (255,255,255), self.place.get_tuple(), 2 )

        val = (self.place.get_right() - self.place.pos.x) * self._value

        slide = Rectangle( self.place.pos.x + val - 1, self.place.pos.y,
                           3, self.place.size.y )
        draw.rect( surface, (255,255,255), slide.get_tuple(), 2 )
        #print self._value

    def value_changed( self ):
        changed = self._old_value <> self._value
        self._old_value = self._value
        return changed

    def get_value( self ):
        return self._value

    def set_value( self, value ):
        if value > 1.0:
            value = 1.0
        if value < 0.0:
            value = 0.0

        self._value = value

    def went_up( self ):
        return self._went_up

class ImageSlider (Slider):
    def __init__( self, pos, sprite, button = None):
        size = sprite.get_size()
        Slider.__init__( self, Rectangle.from_pos_size(pos, Vec2D(size[0], size[1]) ) )

        self.sprite = sprite
        self.button = button

        if button is not None:
            self.add_subcomponent( button )

        self.delegate_active = self.button

    def tick( self, userinput, guistate ):
        # Handle active component
        if guistate.active == self.button or guistate.active == self:
            guistate.active = self.button

        Component.tick( self, userinput, guistate )

        if guistate.active == self.button or guistate.active == self:
            guistate.active = self.button

        # Check if mouse is down on slider or button
        if (userinput.mouse.is_down( Mouse.LEFT ) and \
               (self._is_sliding or self.place.contains( userinput.mouse.pos ))):
##               or \
##               (self.button is not None and self.button.is_down):
            self._value = float(userinput.mouse.pos.x - self.place.pos.x) \
                          / (self.place.get_right() - self.place.pos.x )
            self._value = min(1.0, max(0.0, self._value))
            self._is_sliding = True

        # Handle keys
        STEP = 0.01
        LARGE_STEP = 0.2

        if guistate.active == self.button:
            if userinput.key.is_down( K_LEFT ):
                self.set_value( self.get_value() - STEP )
            if userinput.key.is_down( K_RIGHT ):
                self.set_value( self.get_value() + STEP )
            if userinput.key.any_went_down( Button.SELECT_KEYS ):
                new_value = self.get_value() + LARGE_STEP
                new_value = (int(new_value * 5) / 5.0)
                if new_value > 1.0: new_value = 0.0
                self.set_value( new_value )


        self._went_up = False
        if userinput.mouse.went_up( Mouse.LEFT ) and self._is_sliding:
            self._went_up = True
            self._is_sliding = False

        if userinput.key.any_went_up( [K_LEFT, K_RIGHT] ):
            self._went_up = True

    def draw( self, surface, interpol, time_sec ):
        val = (self.place.right - self.place.left) * self._value

        if self.button is not None:
            self.button.pos = Vec2D(self.place.left + val,
                                    self.place.top + self.place.height / 2)

        rect = Rectangle( 0, 0,
                          val, self.place.height )
        self.sprite.nr = 1
        self.sprite.draw( surface, self.place.pos, rect )

        rect = Rectangle( val, 0,
                          self.place.width - val, self.place.height )
        self.sprite.nr = 0
        pos = self.place.pos + Vec2D(val, 0)
        self.sprite.draw( surface, pos, rect )


        Component.draw( self, surface, interpol, time_sec )


class Label (Component):

    def __init__( self, pos, text = None, font = None, image = None ):
        Component.__init__( self )
        self.pos = pos
        self.text = text
        self.font = font
        self.image = image

    def set_text( self, text ):
        self.text = text

    def get_text( self ):
        return self.text

    def set_image( self, image ):
        self.image = image

    def get_image( self ):
        return self.image

    def draw( self, surface, interpol, time_sec ):
        """Drawing of text not implemented yet!"""
        Component.draw( self, surface, interpol, time_sec )

        if self.image is not None:
            self.image.draw( surface, self.pos )

        if self.text is not None and self.font is not None:
            self.font.draw( self.text, surface, self.pos.get_tuple() )

class TextField (InteractiveComponent):

    def __init__( self, place, font ):
        InteractiveComponent.__init__( self, place )
        self.font = font
        self.text = ""

    def tick( self, userinput, guistate ):
        InteractiveComponent.tick( self, userinput, guistate )

        if self.is_enabled and userinput.mouse.went_down( Mouse.LEFT ) and \
                   self.place.contains( userinput.mouse.pos ):
            self.lock_input( True )

        if guistate.get_active() == self:
            self.text += userinput.key.get_chars()

    def _handle_last_word( self, lines, word, length_pixels ):
        if self.font.get_width( lines[-1] + word ) <= length_pixels:
            lines[-1] += word
            word = " "
        else:
            lines.append( word.strip() )
            word = " "

        return word


    def _wrap_to_lines( self, text, length_pixels ):
        lines = [""]
        word = ""
        for ch in text:
            if ch == "\n" or ch == " ":
                word = self._handle_last_word( lines, word, length_pixels )

                if ch == "\n":
                    lines.append("")

            else:
                word += ch

        word = self._handle_last_word( lines, word, length_pixels)

        return lines


    def _set_text( self, text ):
        self._text = text

        self.lines = self._wrap_to_lines( text, self.place.size.x )


    def _get_text( self ):
        return self._text

    text = property(_get_text, _set_text)

    def draw( self, surface, interpol, time_sec ):
        """Drawing of text not implemented yet!"""
        InteractiveComponent.draw( self, surface, interpol, time_sec )

        #draw.rect( surface, (128,128,128), self.place.get_tuple(), 1 )

        pos = self.place.pos.get_tuple()
        for line in self.lines:
            self.font.draw( line, surface, pos )

            pos = (pos[0], pos[1] + self.font.height)


#!/usr/bin/env python

import pygame
import monorail.koon.gui as gui
import monorail.koon.gfx as gfx
from monorail.koon.input import *
from monorail.koon.geo import Vec2D, Rectangle


def setup_module( cls ):
    pygame.init()

def teardown_module( cls ):
    pygame.quit()


class TestGuiState:

    def test_get_interactive_components_should_return_all_and_no_more( self ):
        """Given a hierarchy of components
        when asked for all interactive components
        then all and no more are returned"""
        # Given
        root = gui.Component()
        child1 = gui.Component()
        child2 = gui.InteractiveComponent( Rectangle(0,0,0,0) )
        child11 = gui.Component()
        child12 = gui.InteractiveComponent( Rectangle(0,0,0,0) )
        child21 = gui.InteractiveComponent( Rectangle(0,0,0,0) )
        child22 = gui.Component()
        child222 = gui.InteractiveComponent( Rectangle(0,0,0,0) )
        
        root.add_subcomponent( child1 )
        root.add_subcomponent( child2 )
        child1.add_subcomponent( child11 )
        child1.add_subcomponent( child12 )
        child2.add_subcomponent( child21 )
        child2.add_subcomponent( child22 )
        child22.add_subcomponent( child222 )

        # When
        interactives = gui.GuiState._get_interactive_components( root )

        # Then
        assert len( interactives ) == 4
        assert root     not in interactives
        assert child1   not in interactives
        assert child2       in interactives
        assert child11  not in interactives
        assert child12      in interactives
        assert child21      in interactives
        assert child22  not in interactives
        assert child222     in interactives

    def test_mouse_move_over_should_activate_component( self ):
        # Given
        gui_state = gui.GuiState()
        userinput = UserInput()        
        userinput.mouse.feed_pos( Vec2D( 50, 150 ) )

        component = gui.InteractiveComponent( Rectangle( 100, 100, 100, 100 ) )

        assert gui_state.get_active() <> component

        # When
        userinput.update()
        userinput.mouse.feed_pos( Vec2D( 150, 150 ) )
        gui_state.update( userinput, component )

        # Then
        assert gui_state.get_active() == component
        

    def test_mouse_still_over_shouldnt_activate_component( self ):
        # Given
        gui_state = gui.GuiState()
        userinput = UserInput()        
        userinput.mouse.feed_pos( Vec2D( 150, 150 ) )

        component1 = gui.InteractiveComponent( Rectangle( 100, 100, 100, 100 ) )
        component = gui.InteractiveComponent( Rectangle( 100, 100, 100, 100 ) )

        base = gui.Component()
        base.add_subcomponent(component1)
        base.add_subcomponent(component)

        assert gui_state.get_active() <> component

        # When
        userinput.update()
        userinput.mouse.feed_pos( Vec2D( 150, 150 ) )
        gui_state.update( userinput, base )

        # Then
        assert gui_state.get_active() <> component

    def test_mouse_move_over_shouldnt_activate_nonhard_component( self ):
        # Given
        gui_state = gui.GuiState()
        userinput = UserInput()        
        userinput.mouse.feed_pos( Vec2D( 50, 150 ) )

        component = gui.InteractiveComponent( Rectangle( 100, 100, 100, 100 ) )

        hardcomp = gui.InteractiveComponent( Rectangle( 100, 300, 100, 100 ) )
        hardcomp.lock_input( True )

        base = gui.Component()
        base.add_subcomponent( component )
        base.add_subcomponent( hardcomp )
        
        gui_state.set_active( hardcomp )

        assert gui_state.get_active() <> component
        assert gui_state.get_active() == hardcomp

        # When
        userinput.update()
        userinput.mouse.feed_pos( Vec2D( 150, 150 ) )
        gui_state.update( userinput, base )

        # Then
        assert gui_state.get_active() <> component
        assert gui_state.get_active() == hardcomp


class TestComponent:

    def test_subs( self ):
        comp = gui.Component()

    def test_should_call_subs_tick( self ):
        """Given a derived Component and subcomponent
            when tick is called on parent
            then tick is also called on subcomponent."""
        class Child (gui.Component):
            def __init__( self ):
                gui.Component.__init__( self )
                self.tick_cnt = 0

            def tick( self, userinput, guistate ):
                gui.Component.tick( self, None, None )
                self.tick_cnt += 1

        # Given
        top = Child()
        sub1 = Child()
        sub2 = Child()
        sub1sub = Child()
        top.add_subcomponent( sub1 )
        top.add_subcomponent( sub2 )
        sub1.add_subcomponent( sub1sub )
        assert top.tick_cnt == 0
        assert sub1.tick_cnt == 0
        assert sub2.tick_cnt == 0
        assert sub1sub.tick_cnt == 0

        # When
        top.tick( None, None )

        # Then
        assert sub1.tick_cnt == 1
        assert sub2.tick_cnt == 1
        assert sub1sub.tick_cnt == 1
                    
    def test_should_call_subs_draw( self ):
        """Given a derived Component and subcomponent
            when draw is called on parent
            then draw is also called on subcomponent."""
        class Child (gui.Component):
            def __init__( self ):
                gui.Component.__init__( self )
                self.draw_cnt = 0

            def draw( self, surface, interpol, time_sec ):
                gui.Component.draw( self, surface, interpol, time_sec )
                self.draw_cnt += 1

        # Given
        top = Child()
        sub1 = Child()
        sub2 = Child()
        sub1sub = Child()
        top.add_subcomponent( sub1 )
        top.add_subcomponent( sub2 )
        sub1.add_subcomponent( sub1sub )
        assert top.draw_cnt == 0
        assert sub1.draw_cnt == 0
        assert sub2.draw_cnt == 0
        assert sub1sub.draw_cnt == 0

        # When
        top.draw( None, 0, 0 )

        # Then
        assert sub1.draw_cnt == 1
        assert sub2.draw_cnt == 1
        assert sub1sub.draw_cnt == 1
        

class TestButton:

    def test_init( self ):
        button = gui.Button()

    def test_clicked_when_mousepress_inside( self ):
        """Given a button
            when mouse clicks inside
            then button should return clicked state"""
        # Given
        button = gui.Button( Rectangle( 100, 100 , 50, 50 ) )
        userinput = UserInput()
        guistate = gui.GuiState()
        assert not button.went_down()

        # When
        userinput.mouse.feed_pos( Vec2D(110,110) )
        userinput.mouse.feed_down( Mouse.LEFT )
        button.tick( userinput, guistate )
        
        # Then
        assert button.went_down()

    def test_not_clicked_when_mousepress_outside( self ):
        """Given a button
            when mouse clicks outside
            then button shouldn't return clicked state"""
        # Given
        button = gui.Button( Rectangle( 100, 100 , 50, 50 ) )
        userinput = UserInput()
        guistate = gui.GuiState()
        assert not button.went_down()

        # When
        userinput.mouse.feed_pos( Vec2D(110,90) )
        userinput.mouse.feed_down( Mouse.LEFT )
        button.tick( userinput, guistate )
        
        # Then
        assert not button.went_down()

    def test_not_clicked_when_mouserelease_inside( self ):
        """Given a button
            when mouse is released inside
            then button shouldn't return clicked state"""
        # Given
        button = gui.Button( Rectangle( 100, 100 , 50, 50 ) )
        userinput = UserInput()
        guistate = gui.GuiState()
        assert not button.went_down()

        # When
        userinput.mouse.feed_pos( Vec2D(110,90) )
        userinput.mouse.feed_down( Mouse.LEFT )
        userinput.update()
        userinput.mouse.feed_up( Mouse.LEFT )
        button.tick( userinput, guistate )
        
        # Then
        assert not button.went_down()

    def test_clicked_when_enter_activated( self ):
        """Given an active button
            when enter is pressed
            then button should return clicked state"""
        pass

    def test_not_clicked_when_enter_non_activated( self ):
        """Given a non-active button
            when enter is pressed
            then button shouldn't return clicked state"""
        pass

class TestImageButton:

    def test_init( self ):
        surface = gfx.Surface( (10, 10 * 4) )
        
        sprite = gfx.SpriteFilm( surface )
        sprite.set_div( 1, 4 )
        assert sprite.width == 10 and sprite.height == 10
        
        button = gui.ImageButton(sprite)    

    def test_draw( self ):
        surface = gfx.Surface( (10, 10 * 3) )
        
        sprite = gfx.SpriteFilm( surface )
        sprite.set_div( 1, 3 )
        assert sprite.width == 10 and sprite.height == 10
        
        button = gui.ImageButton(sprite)

        background = gfx.Surface((100,100))

        button.draw( background, 0, 0 )

class TestCheckbox:
    def test_init( self ):
        checkbox = gui.Checkbox()

    def test_init_selected( self ):
        checkbox = gui.Checkbox()
        assert not checkbox.is_selected()

        checkbox = gui.Checkbox( selected = True )
        assert checkbox.is_selected()

    def test_clicked_when_mousepress_inside( self ):
        # Given
        checkbox = gui.Checkbox( Rectangle( 100, 100 , 50, 50 ), False )
        userinput = UserInput()
        guistate = gui.GuiState()
        assert not checkbox.is_selected()

        # When
        userinput.mouse.feed_pos( Vec2D(110,110) )
        userinput.mouse.feed_down( Mouse.LEFT )
        checkbox.tick( userinput, guistate )
        
        # Then
        assert checkbox.went_down()
        assert checkbox.is_selected()

        # And when
        checkbox.tick( userinput, guistate )

        # Then
        assert not checkbox.is_selected()

class TestImageCheckbox:
    pass

class TestRadiobuttons:

    def test_init( self ):
        radiobuttons = gui.Radiobuttons()

    def test_add( self ):
        # Given
        rb = gui.Radiobuttons()
        checkbox1 = gui.Checkbox()
        checkbox2 = gui.Checkbox()

        # When
        rb.append( checkbox1 )
        rb.append( checkbox2 )

        # Then
        assert len( rb ) == 2
        assert rb[0] is checkbox1
        assert rb[1] is checkbox2

    def test_only_one_selected( self ):
        # Given
        rb = gui.Radiobuttons()
        rb.append( gui.Checkbox( Rectangle( 100, 100 , 50, 50 ), False ) )
        rb.append( gui.Checkbox( Rectangle( 100, 200 , 50, 50 ), False ) )
        rb.append( gui.Checkbox( Rectangle( 100, 300 , 50, 50 ), False ) )
        userinput = UserInput()
        guistate = gui.GuiState()

        # When select checkbox 0
        userinput.mouse.feed_pos( Vec2D(110,110) )
        userinput.mouse.feed_down( Mouse.LEFT )
        rb.tick( userinput, guistate )
        
        # Then
        assert rb[0].is_selected()
        assert not rb[1].is_selected()
        assert not rb[2].is_selected()
        assert rb.get_selected() is rb[0]
        assert rb.get_selected_index() == 0

        # And when select checkbox 2
        userinput.mouse.feed_pos( Vec2D(110,310) )
        userinput.mouse.feed_down( Mouse.LEFT )
        rb.tick( userinput, guistate )
        
        # Then
        assert not rb[0].is_selected()
        assert not rb[1].is_selected()
        assert rb[2].is_selected()
        assert rb.get_selected() is rb[2]
        assert rb.get_selected_index() == 2

        # And when select checkbox 1
        userinput.mouse.feed_pos( Vec2D(110,210) )
        userinput.mouse.feed_down( Mouse.LEFT )
        rb.tick( userinput, guistate )
        
        # Then
        assert not rb[0].is_selected()
        assert rb[1].is_selected()
        assert not rb[2].is_selected()
        assert rb.get_selected() is rb[1]
        assert rb.get_selected_index() == 1

        
class TestTextField:

    def test_get_text_returns_set_text( self ):
        """Given a TextField
            when a text is set
            then that text can be retrieved"""
        # Given
        textfield = gui.TextField( Rectangle( 100, 100, 50, 50 ), gfx.Font() )
        TEST_TEXT = "Testing 1 2 3"

        # When
        textfield.text = TEST_TEXT

        # Then
        assert textfield.text == TEST_TEXT
        
    def test_active_receives_input_chars( self ):
        """Given an active TextField
            when keys are pressed
            then the text is entered"""
        # Given
        textfield = gui.TextField( Rectangle( 100, 100, 50, 50 ), gfx.Font() )        
        userinput = UserInput()
        guistate = gui.GuiState()
        guistate.set_active( textfield )
        
        # When
        # loop 1
        userinput.key.feed_char( "A" )
        textfield.tick( userinput, guistate )
        userinput.update()
        userinput.key.feed_char( "b" )
        textfield.tick( userinput, guistate )
        userinput.update()        
        
        # Then
        assert textfield.text == "Ab"
        
    def test_non_active_receives_no_input( self ):
        """Given an non-active TextField
            when keys are pressed
            then the text isn't entered"""
        # Given
        textfield = gui.TextField( Rectangle( 100, 100, 50, 50 ), gfx.Font() )        
        userinput = UserInput()
        guistate = gui.GuiState()
        guistate.set_active( None )
        
        # When
        # loop 1
        userinput.key.feed_char( "A" )
        textfield.tick( userinput, guistate )
        userinput.update()
        userinput.key.feed_char( "b" )
        textfield.tick( userinput, guistate )
        userinput.update()        
        
        # Then
        assert textfield.text == ""
        

class TestSlider:

    def test_init( self ):
        slider = gui.Slider()

        

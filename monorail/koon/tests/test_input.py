#!/usr/bin/env python

from monorail.koon.input import *
from monorail.koon.geo import Vec2D
from pygame.locals import *

class TestKeyboard:

    def test_lifecycle( self ):
        key = Keyboard()

        key.feed_down( K_a )
        
        assert key.went_down( K_a )
        assert not key.went_down( K_b )
        assert not key.went_up( K_a )
        assert key.went_down( K_a )
        assert key.is_down( K_a )

        key.update()

        assert not key.went_down( K_a )
        assert key.is_down( K_a )

        key.feed_up( K_a )

        assert not key.went_down( K_a )
        assert key.went_up( K_a )
        assert not key.is_down( K_a )
        assert key.went_up( K_a )

    def test_char_buffer( self ):
        key = Keyboard()

        key.update()
        key.feed_char("T")
        key.feed_char("e")

        assert key.get_chars() == "Te"

        key.update()

        key.feed_char("s")
        key.feed_char("t")

        assert key.get_chars() == "st"
        
class TestMouse:

    def test_buttons( self ):
        mouse = Mouse()

        mouse.feed_down( Mouse.LEFT )
        
        assert mouse.went_down( Mouse.LEFT )
        assert not mouse.went_down( Mouse.RIGHT )
        assert not mouse.went_up( Mouse.LEFT )
        assert mouse.went_down( Mouse.LEFT )
        assert mouse.is_down( Mouse.LEFT )

        mouse.update()

        assert not mouse.went_down( Mouse.LEFT )
        assert mouse.is_down( Mouse.LEFT )

        mouse.feed_up( Mouse.LEFT )

        assert not mouse.went_down( Mouse.LEFT )
        assert mouse.went_up( Mouse.LEFT )
        assert not mouse.is_down( Mouse.LEFT )
        assert mouse.went_up( Mouse.LEFT )


    def test_pos( self ):
        mouse = Mouse()

        mouse.feed_pos( Vec2D(123, 321) )
        assert mouse.pos == Vec2D( 123, 321 )

    def test_has_moved_returns_false_when_not_moved( self ):
        # Given
        mouse = Mouse()
        mouse.feed_pos( Vec2D( 33, 44 ) )        

        # When
        mouse.update()
        mouse.feed_pos( Vec2D( 33, 44 ) )

        # Then
        assert not mouse.has_moved()

    def test_has_moved_returns_true_when_moved( self ):
        # Given
        mouse = Mouse()
        mouse.feed_pos( Vec2D( 33, 44 ) )        

        # When
        mouse.update()
        mouse.feed_pos( Vec2D( 55, 44 ) )

        # Then
        assert mouse.has_moved()

        

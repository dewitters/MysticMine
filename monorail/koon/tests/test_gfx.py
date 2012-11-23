#!/usr/bin/env python

from source.koon.gfx import *;
import pygame

class TestFont:

    def setup_class( cls ):
        pygame.init()

    def teardown_class( cls ):
        pygame.quit()

    def test_constructors( self ):
        font = Font()
        font = Font( size=20 )

    def test_set_size( self ):
        font = Font( size=20 )
        font.set_size( 16 )

    def test_set_color( self ):
        font = Font( size=20, color=(0,2,3) )
        font.set_color( (255,255,255) )

    def test_antialias( self ):
        font = Font( use_antialias = False )
        assert font.use_antialias() == False
        font.set_antialias( True )
        assert font.use_antialias() == True

    def test_draw( self ):
        surface = Surface( (400, 400) )
        font = Font( size=20 )
        font.draw( "Testje", surface, (10, 10) )


class TestTimer:

    def test_times_run_equals_hertz( self ):
        """Given a timer on 2 hertz
           When 1 second ellapses
           Then it is run 2 times"""
        # Given
        timer = Timer( 2 )
        
        # When
        timer.start( 20 )
        
        # Then
        assert timer.do_tick( 21 )
        assert timer.do_tick( 21 )
        assert not timer.do_tick( 21 )
        assert not timer.do_tick( 21 )

        assert timer.do_tick( 22 )
        assert timer.do_tick( 22 )
        assert not timer.do_tick( 22 )
        assert not timer.do_tick( 22 )
        assert not timer.do_tick( 22 )
        
        assert timer.do_tick( 24 )
        assert timer.do_tick( 24 )
        assert timer.do_tick( 24 )
        assert timer.do_tick( 24 )
        assert not timer.do_tick( 24 )

    def test_when_not_called_start( self ):
        """Given a timer
           When start wasn't called
           Then the first do_tick initializes the timer"""
        # Given
        timer = Timer( 2 )

        # When start isn't called

        # Then
        assert timer.do_tick( 30 )
        assert not timer.do_tick ( 30 )
        assert not timer.do_tick ( 30 )

        assert timer.do_tick( 31 )
        assert timer.do_tick( 31 )
        assert not timer.do_tick ( 31 )
        assert not timer.do_tick ( 31 )

class TestLoopAnimationTimer:

    def test_fps_later_when_time_ellapses( self ):
        """Given an animation timer on 2 fps
           When 1 second ellapses
           Then it is 2 frames later"""
        # Given
        anim = LoopAnimationTimer( 2, 0, 100 )
        
        # When
        anim.set_frame( 10, 4 )
        
        # Then
        assert anim.get_frame( 10 ) == 4
        assert anim.get_frame( 11 ) == 6
        assert anim.get_frame( 13 ) == 10

    def test_anim_cycles_on_time( self ):
        """Given an animation timer on 2 fps with 4 max frames
           When 2 seconds pass by
           Then the animation will restart from frame 0"""
        # Given
        anim = LoopAnimationTimer( 2, 0, 4 )

        # When
        anim.set_frame( 0, 0 )

        # Then
        assert anim.get_frame( 1 ) == 2
        assert anim.get_frame( 2 ) == 0
        assert anim.get_frame( 3 ) == 2
        assert anim.get_frame( 4 ) == 0

    def test_anim_cycles_on_time( self ):
        """Given an animation timer on 2 fps with 4 max frames
           When animation starts on frame 2 and 1 seconds pass by
           Then the animation will restart from frame 0"""
        # Given
        anim = LoopAnimationTimer( 2, 0, 4 )

        # When
        anim.set_frame( 0, 2 )

        # Then
        assert anim.get_frame( 1 ) == 0

    def test_when_not_called_set_frame( self ):
        """Given an animation timer
           When user didn't set start frame with set_frame()
           Then starttime = 0 is used"""
        # Given
        anim = LoopAnimationTimer( 2, 0, 100 )

        # When not calling set_frame()

        # Then
        assert anim.get_frame( 0 ) == 0
        assert anim.get_frame( 1 ) == 2

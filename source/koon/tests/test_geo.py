#!/usr/bin/env python

from source.koon.geo import *
import pygame

class TestRectangle:

    def test_intersect( cls ):
        a = Rectangle( 50, 50, 100, 100 )
        b = Rectangle( 60, 60, 90, 90 )
        c = Rectangle( 40, 40, 20, 20 )

        assert (a & b) == b
        assert (b & a) == b
        assert (a & c) == Rectangle(50, 50, 10, 10)


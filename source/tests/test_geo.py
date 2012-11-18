#!/usr/bin/env python

from source.koon.geo import Vec3D

class TestVec3D:
    def test_constructor( self ):
        a = Vec3D()
        b = Vec3D( z = 1 )
        c = Vec3D( 3, 2, 1 )
        assert a.x == b.x
        assert a.z != b.z
        assert c.z == b.z

    def test_eq( self ):
        a = Vec3D( 1, 2, 3 )
        b = Vec3D( 3, 2, 1 )
        c = Vec3D( 1, 2, 3 )
        assert a == c
        assert a <> b
        
    def test_add_sub_mul( self ):
        a = Vec3D( 1, 1, 0 )
        b = Vec3D( 0, 2, 3 )
        assert a + b == Vec3D( 1, 3, 3 )
        assert a - b == Vec3D( 1, -1, -3 )
        assert b * 5 == Vec3D( 0, 10, 15 )
        assert -b == Vec3D( 0, -2, -3 )
        assert Vec3D( 2, 8, 34 ) / 2 == Vec3D( 1, 4, 17 )
        
    def test_dot_product( self ):
        a = Vec3D( 1, 1, 0 )
        b = Vec3D( 1, -1, 0 )
        assert a.dot( b ) == 0

        a = Vec3D( 4, 1, 5 )
        b = Vec3D( 1, -2, 3 )
        assert a.dot( b ) == b.dot( a )

    def test_cross_product( self ):
        a = Vec3D( 4, 1, 5 )
        b = Vec3D( 1, -2, 3 )
        c = a.cross( b )
        assert a.cross( b ) == -b.cross( a )
        assert a.dot( c ) == 0
        assert b.dot( c ) == 0

    def test_length( self ):
        a = Vec3D( 0, 24, 0 )
        assert a.length() == 24

        b = Vec3D( -23, 21, 5 )
        assert b.length() * 5 == (b*5).length()

    def test_normalize( self ):
        a = Vec3D( 23, -1, 32 )
        assert abs(a.normalize().length() - 1) <= 0.000000000001


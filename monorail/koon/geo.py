"""Geometric classes and functions
"""

from math import sqrt

class Vec3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __add__(self, other):
        return Vec3D( self.x + other.x, self.y + other.y, self.z + other.z )
    
    def __sub__(self, other):
        return Vec3D( self.x - other.x, self.y - other.y, self.z - other.z )
    
    def __mul__(self, factor):
        return Vec3D( self.x * factor, self.y * factor, self.z * factor )

    def __div__(self, factor):
        return Vec3D( self.x / factor, self.y / factor, self.z / factor )

    def __neg__(self):
        return Vec3D( -self.x, -self.y, -self.z )
    
    def dot( self, other ):
        """returns dot product of 2 vectors"""
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross( self, other ):
        """returns cross produt of 2 vectors"""
        return Vec3D(  (self.y * other.z) - (self.z * other.y), \
                       (self.z * other.x) - (self.x * other.z), \
                       (self.x * other.y) - (self.y * other.x) )

    def length( self ):
        return sqrt( self.length2() )

    def length2( self ):
        """returns the vector length ** 2 (way faster than len())"""
        return self.dot( self )

    def normalize( self ):
        """returns the normalized vector"""
        return self / self.length()

    def __str__( self ):
        return "("+ str(self.x) +","+ str(self.y) +","+ str(self.z) +")"


class Vec2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __add__(self, other):
        return Vec2D( self.x + other.x, self.y + other.y )
    
    def __sub__(self, other):
        return Vec2D( self.x - other.x, self.y - other.y )
    
    def __mul__(self, factor):
        return Vec2D( self.x * factor, self.y * factor )

    def __div__(self, factor):
        return Vec2D( self.x / factor, self.y / factor )

    def __neg__(self):
        return Vec2D( -self.x, -self.y )
    
    def dot( self, other ):
        """returns dot product of 2 vectors"""
        return (self.x * other.x) + (self.y * other.y)

    def length( self ):
        return sqrt( self.length2() )

    def length2( self ):
        """returns the vector length ** 2 (way faster than len())"""
        return self.dot( self )

    def normalize( self ):
        """returns the normalized vector"""
        return self / self.length()

    def get_tuple( self ):
        return (self.x, self.y)

    def __str__( self ):
        return "("+ str(self.x) +","+ str(self.y) +")"

class Rectangle:
    def __init__( self, x, y, width, height ):
        self.pos = Vec2D( x, y )
        self.size = Vec2D( width, height )        

    @staticmethod
    def from_pos_size( pos, size ):
        return Rectangle(pos.x, pos.y, size.x, size.y)

    @staticmethod
    def from_tuple( tup ):
        return Rectangle(tup[0], tup[1], tup[2], tup[3])    

    def contains( self, pos ):
        return pos.x >= self.pos.x and \
               pos.y >= self.pos.y and \
               pos.x < self.get_right() and \
               pos.y < self.get_bottom()

    def get_right( self ):
        return self.pos.x + self.size.x
    right = property( get_right )

    def get_bottom( self ):
        return self.pos.y + self.size.y
    bottom = property( get_bottom )

    left = property( lambda self: self.pos.x )
    top = property( lambda self: self.pos.y )

    width  = property( lambda self: self.size.x )
    height = property( lambda self: self.size.y )

    def get_tuple( self ):
        return (self.pos.x, self.pos.y, self.size.x, self.size.y)

    def __and__( self, other ):
        """Intersect"""
        x = max( self.pos.x, other.pos.x )
        y = max( self.pos.y, other.pos.y )
        right = min( self.right, other.right )
        bottom = min( self.bottom, other.bottom )

        return Rectangle(x, y, right-x, bottom-y)
            

    def __eq__( self, other ):
        return self.pos == other.pos and self.size == other.size

    def __str__( self ):
        return "Rectangle(%d,%d,%d,%d)" % (self.pos.x, self.pos.y, self.size.x, self.size.y)


def lin_ipol( value, a, b, begin = 0.0, end = 1.0 ):
    return a + (float(value - begin) * float(b - a)) / float(end - begin)

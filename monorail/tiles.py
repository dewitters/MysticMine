"""Tiles, trails, etc.
"""

import math
import struct
import copy
from random import randint

import pygame

from koon.geo import Vec3D, Vec2D
from koon.res import resman


class Direction:
    """A wind direction

    Don't use constructors, but use:
    Direction.NORTH
    Direction.EAST
    Direction.SOUTH
    Direction.WEST

        N  E         x
         \/        \/
         /\        /\
        W  S         y
    """

    def __init__( self, dir_id ):
        """Don't use contructor!"""
        self.id = dir_id

    def __eq__( self, other ):
        return self.id == other.id

    def __ne__( self, other ):
        return self.id <> other.id

    def get_opposite( self ):
        return Direction( (self.id + 2) % 4 )

    def __hash__( self ):
        return hash( self.id )

Direction.NORTH = Direction( 0 )
Direction.EAST  = Direction( 1 )
Direction.SOUTH = Direction( 2 )
Direction.WEST  = Direction( 3 )
Direction.ALL = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]


class Trail:
    """Trail class is part of Tile

    Don't use this class straight away, but use it in combination with Tile

    Public members:
    - type: the trail type (see Trail.Type)
    - may_switch: True if able to switch, False if not
    """

    class Type:
        NS, EW, SE, SW, NW, NE, HILL, MAX = range( 8 )

    def __init__( self, tile, trail_type = Type.NS  ):
        self.tile = tile
        self.type = trail_type
        self.may_switch = True

    def get_in_direction( self ):
        """returns the highest direction"""
        if self.tile.type == Tile.Type.FLAT:
            if self.type in [Trail.Type.NS, Trail.Type.NE, Trail.Type.NW]:
                return Direction.NORTH
            elif self.type in [Trail.Type.EW, Trail.Type.SE]:
                return Direction.EAST
            elif self.type == Trail.Type.SW:
                return Direction.SOUTH;
            else:
                assert False # Trail type not defined!
                return Direction.NORTH

        elif self.tile.type in [Tile.Type.NORTH_SLOPE_BOT, Tile.Type.NORTH_SLOPE_TOP]:
            return Direction.NORTH

        elif self.tile.type in [Tile.Type.EAST_SLOPE_BOT, Tile.Type.EAST_SLOPE_TOP]:
            return Direction.EAST

        elif self.tile.type in [Tile.Type.SOUTH_SLOPE_BOT, Tile.Type.SOUTH_SLOPE_TOP]:
            return Direction.SOUTH

        elif self.tile.type in [Tile.Type.WEST_SLOPE_BOT, Tile.Type.WEST_SLOPE_TOP]:
            return Direction.WEST

        else:
            assert False # Tile type not defined!
            return Direction.NORTH

    def get_out_direction( self ):
        """returns the lowest direction"""
        if self.tile.type == Tile.Type.FLAT:
            if self.type in [Trail.Type.NW, Trail.Type.EW, Trail.Type.SW]:
                return Direction.WEST
            elif self.type in [Trail.Type.NS, Trail.Type.SE]:
                return Direction.SOUTH
            elif self.type == Trail.Type.NE:
                return Direction.EAST
            else:
                assert False # Trail type not defined
                return Direction.WEST
        else:
            return self.get_in_direction().get_opposite();

    def is_switch( self ):
        return self.tile.type == Tile.Type.FLAT and \
               self.tile.neighbors.count( None ) < 2

    def switch_it( self, from_dir = None ):
        if not self.may_switch: return

        available = self.tile.get_possible_switches( from_dir )
        if len( available ) == 0: return

        i = 5
        try:
            i = available.index( self.type )
        except: pass

        if i+1 >= len( available ):
            self.type = available[0]
        else:
            self.type = available[i+1]

    def align( self, direction = None ):
        if self.tile.type <> Tile.Type.FLAT : return

        if isinstance(self.tile, Enterance):
            if self.tile.is_north_exit():
                self.type = Trail.Type.NS
            else:
                self.type = Trail.Type.EW
        else:
            if direction is None:
                available = self.tile.get_possible_switches()
                if self.type not in available:
                    self.switch_it()
            else:
                if direction <> self.get_in_direction() and direction <> self.get_out_direction():
                    self.switch_it( direction )


class Tile:
    """Tile class

    public members:
    - pos:       the tile position
    - type :     the tile type
    - trail
    - neighbors
    - pickup:    None if no pickup available
    - is_selected
    """
    class Type:
        FLAT, NORTH_SLOPE_TOP, NORTH_SLOPE_BOT, EAST_SLOPE_TOP, EAST_SLOPE_BOT, \
        SOUTH_SLOPE_TOP, SOUTH_SLOPE_BOT, WEST_SLOPE_TOP, WEST_SLOPE_BOT, MAX, \
        ENTERANCE, RAILGATE = range( 12 )
        # NORTH_SLOPE_TOP is going down north to south

    def __init__( self, position, tile_type, trail_type = None ):
        # init trail type
        if trail_type is None:
            if tile_type == Tile.Type.FLAT:
                trail_type = Trail.Type.NS
            else:
                trail_type = Trail.Type.HILL

        #assert (tile_type == Tile.Type.FLAT) or (trail_type == Trail.Type.HILL)

        self.pos = position
        self.type = tile_type
        self.trail = Trail( self, trail_type )
        self.pickup = None
        self.is_selected = False

        self.neighbors = [None, None, None, None] # North, east, south, west

    def get_length( self ):
        if self.type == Tile.Type.FLAT:
            if self.trail.type in [Trail.Type.NS, Trail.Type.EW]:
                return 1000;
            else:
                return int( (0.5 * math.pi / 2.0) * 1000 )
        else:
            return 2300 / 2

    def get_angle( self ):
        if self.type == Tile.Type.FLAT:
            return 0
        else:
            return 8

    def set_neighbor( self, neighbor_tile, direction ):
        self.neighbors[ direction.id ] = neighbor_tile

    def get_neighbor( self, direction ):
        return self.neighbors[ direction.id ]

    def get_in_tile( self ):
        return self.get_neighbor( self.trail.get_in_direction() )

    def get_out_tile( self ):
        return self.get_neighbor( self.trail.get_out_direction() )

    def get_neighbor_offset( self, direction ):
        if direction == Direction.NORTH:
            offset = Vec3D(0,-1,0)
        elif direction == Direction.EAST:
            offset = Vec3D(1,0,0)
        elif direction == Direction.SOUTH:
            offset = Vec3D(0,1,0)
        elif direction == Direction.WEST:
            offset = Vec3D(-1,0,0)

        if self.type == Tile.Type.NORTH_SLOPE_TOP:
            if direction == Direction.NORTH:
                offset = Vec3D(-1,0,0)
            elif direction in [Direction.EAST, Direction.WEST]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.NORTH_SLOPE_BOT:
            if direction == Direction.SOUTH:
                offset = Vec3D(1,0,0)
            elif direction in [Direction.EAST, Direction.WEST]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.EAST_SLOPE_TOP:
            if direction == Direction.EAST:
                offset = Vec3D(0,1,0)
            elif direction in [Direction.SOUTH, Direction.NORTH]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.EAST_SLOPE_BOT:
            if direction == Direction.WEST:
                offset = Vec3D(0,-1,0)
            elif direction in [Direction.SOUTH, Direction.NORTH]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.SOUTH_SLOPE_TOP:
            if direction == Direction.SOUTH:
                offset = Vec3D(-1,2,0)
            elif direction in [Direction.EAST, Direction.WEST]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.SOUTH_SLOPE_BOT:
            if direction == Direction.NORTH:
                offset = Vec3D(1,-2,0)
            elif direction in [Direction.EAST, Direction.WEST]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.WEST_SLOPE_TOP:
            if direction == Direction.WEST:
                offset = Vec3D(-2,1,0)
            elif direction in [Direction.SOUTH, Direction.NORTH]:
                offset = Vec3D(0,0,0)

        elif self.type == Tile.Type.WEST_SLOPE_BOT:
            if direction == Direction.EAST:
                offset = Vec3D(2,-1,0)
            elif direction in [Direction.SOUTH, Direction.NORTH]:
                offset = Vec3D(0,0,0)

        return offset

    def get_center( self ):
        return ( self.pos.x * 32  + self.pos.y * 32 + 32,
                -self.pos.x * 16  + self.pos.y * 16 + 16 )

    def get_screen_position( self, length ):
        """Returns tuple (x,y) of the position"""
        in_dir = self.trail.get_in_direction()
        out_dir = self.trail.get_out_direction()

        if in_dir == Direction.NORTH:
            if self.type == Tile.Type.NORTH_SLOPE_TOP: in_pos = Vec2D(-16, 8)
            else: in_pos = Vec2D(-16, -8)
        elif in_dir == Direction.EAST:
            if self.type == Tile.Type.EAST_SLOPE_TOP: in_pos = Vec2D(16, 8)
            else: in_pos = Vec2D(16,-8)
        elif in_dir == Direction.SOUTH:
            if self.type == Tile.Type.SOUTH_SLOPE_TOP: in_pos = Vec2D(16, 24)
            else: in_pos = Vec2D(16,8)
        elif in_dir == Direction.WEST:
            if self.type == Tile.Type.WEST_SLOPE_TOP: in_pos = Vec2D(-16, 24)
            else: in_pos = Vec2D(-16, 8)

        if out_dir == Direction.NORTH:
            if self.type == Tile.Type.SOUTH_SLOPE_BOT: out_pos = Vec2D(-16, -24)
            else: out_pos = Vec2D(-16, -8)
        elif out_dir == Direction.EAST:
            if self.type == Tile.Type.WEST_SLOPE_BOT: out_pos = Vec2D(16, -24)
            else: out_pos = Vec2D(16,-8)
        elif out_dir == Direction.SOUTH:
            if self.type == Tile.Type.NORTH_SLOPE_BOT: out_pos = Vec2D(16, -8)
            else: out_pos = Vec2D(16,8)
        elif out_dir == Direction.WEST:
            if self.type == Tile.Type.EAST_SLOPE_BOT: out_pos = Vec2D(-16, -8)
            else: out_pos = Vec2D(-16, 8)


        if in_dir == out_dir.get_opposite():
            pos = (in_pos * (self.get_length() - length) + out_pos * length) / self.get_length()
        else:
            interpol = float(length) / float( self.get_length() )
            pos = in_pos - in_pos * math.sin( math.pi * interpol / 2.0 )
            pos += out_pos * (1.0 - math.cos( math.pi * interpol / 2.0))

        pos += Vec2D( self.pos.x * 32  + self.pos.y * 32 + 32,
                -self.pos.x * 16  + self.pos.y * 16 + 16 )

        return pos.get_tuple()

    def get_possible_switches( self, from_dir = None ):
        """Returns the possible trail types"""
        available = []

        if self.get_neighbor( Direction.NORTH ) <> None and self.get_neighbor( Direction.SOUTH ) <> None:
            if from_dir is None or from_dir == Direction.NORTH or from_dir == Direction.SOUTH:
                available.append( Trail.Type.NS )

        if self.get_neighbor( Direction.EAST ) <> None and self.get_neighbor( Direction.WEST ) <> None:
            if from_dir is None or from_dir == Direction.EAST or from_dir == Direction.WEST:
                available.append( Trail.Type.EW )

        if self.get_neighbor( Direction.SOUTH ) <> None and self.get_neighbor( Direction.EAST ) <> None:
            if from_dir is None or from_dir == Direction.SOUTH or from_dir == Direction.EAST:
                available.append( Trail.Type.SE )

        if self.get_neighbor( Direction.SOUTH ) <> None and self.get_neighbor( Direction.WEST ) <> None:
            if from_dir is None or from_dir == Direction.SOUTH or from_dir == Direction.WEST:
                available.append( Trail.Type.SW )

        if self.get_neighbor( Direction.NORTH ) <> None and self.get_neighbor( Direction.WEST ) <> None:
            if from_dir is None or from_dir == Direction.NORTH or from_dir == Direction.WEST:
                available.append( Trail.Type.NW )

        if self.get_neighbor( Direction.NORTH ) <> None and self.get_neighbor( Direction.EAST ) <> None:
            if from_dir is None or from_dir == Direction.NORTH or from_dir == Direction.EAST:
                available.append( Trail.Type.NE )

        return available;


    DATA_FORMAT = "<BBxxiii" # type, trail_type, pos_x, pos_y, pos_z

    def save( self, out_file ):
        data = struct.pack( Tile.DATA_FORMAT, self.type, self.trail.type, self.pos.x, self.pos.y, self.pos.z )
        out_file.write( data )

    @staticmethod
    def load( in_file ):
        data = in_file.read( struct.calcsize( Tile.DATA_FORMAT ) )
        data = struct.unpack( Tile.DATA_FORMAT, data )
        #print "tile load", data[0], data[1], data[2], data[3], data[4]
        if data[0] == Tile.Type.ENTERANCE:
            return Enterance( Vec3D(data[2], data[3], data[4]), data[1] )
        elif data[0] == Tile.Type.RAILGATE:
            return RailGate( Vec3D(data[2], data[3], data[4]), data[1] )
        else:
            return Tile( Vec3D(data[2], data[3], data[4]), data[0], data[1] )

    def set_selected( self, enable ):
        self.is_selected = enable

    def game_tick( self ):
        if self.pickup is not None:
            self.pickup.game_tick()

    def is_switch( self ):
        return self.trail.is_switch()

    def switch_it( self, from_dir = None ):
        self.trail.switch_it( from_dir )

class Enterance( Tile ):
    def __init__( self, position, trail_type = None ):
        Tile.__init__( self, position, Tile.Type.FLAT, trail_type )

    def save( self, out_file ):
        data = struct.pack( Tile.DATA_FORMAT, Tile.Type.ENTERANCE, self.trail.type, self.pos.x, self.pos.y, self.pos.z )
        out_file.write( data )

    def set_portals( self, portals ):
        self.portals = portals

    def get_portals( self ):
        return self.portals

    def get_random_portal( self ):
        return self.portals[ randint(0,len(self.portals)-1) ]

    def is_north_exit( self ):
        return self.neighbors[Direction.SOUTH.id] is not None

class RailGate( Tile ):
    def __init__( self, position, trail_type = None ):
        Tile.__init__( self, position, Tile.Type.FLAT, trail_type )
        self.is_down = False

    def game_tick( self ):
        Tile.game_tick( self )

    def save( self, out_file ):
        data = struct.pack( Tile.DATA_FORMAT, Tile.Type.RAILGATE, self.trail.type, self.pos.x, self.pos.y, self.pos.z )
        out_file.write( data )

    def is_switch( self ):
        return True

    def switch_it( self, from_dir = None ):
        self.is_down = not self.is_down


class TrailPosition:
    """Specifies a position on a trail

    Public Members:
    - tile: the current tile
    - progress: where on the tile
    """

    def __init__( self, tile, progress ):
        self.tile = tile
        self.progress = progress
        self.reversed = 1 # to keep addition consistent (always 1 or -1)

    def set_position( self, tile, progress ):
        self.tile = tile
        self.progress = progress

        while self.progress < 0 or self.progress > self.tile.get_length():
            old_tile = self.tile;
            if self.progress < 0:
                self.tile = self.tile.get_in_tile()

                if self.tile is None:
                    self.tile = old_tile
                    self.progress *= -1
                    self.reverse_progress()
                elif self.tile.get_in_tile() == old_tile:
                    self.progress *= -1
                    self.reverse_progress()
                elif self.tile.get_out_tile() == old_tile:
                    self.progress = self.tile.get_length() + self.progress
                else:
                    self.tile = old_tile
                    self.reverse_progress()
                    self.progress *= -1

            elif self.progress > self.tile.get_length():
                self.progress -= old_tile.get_length()
                self.tile = self.tile.get_out_tile()

                if self.tile is None:
                    self.tile = old_tile
                    self.reverse_progress()
                elif self.tile.get_in_tile() == old_tile:
                    pass
                elif self.tile.get_out_tile() == old_tile:
                    self.progress = self.tile.get_length() - self.progress
                    self.reverse_progress()
                else:
                    self.tile = old_tile
                    self.reverse_progress()
                    self.progress = self.tile.get_length() - self.progress

    def reverse_progress( self ):
        self.reversed *= -1

    def is_reversed( self ):
        return self.reversed == -1

    def __add__( self, distance ):
        pos = copy.copy( self )
        pos.set_position( pos.tile, pos.progress + distance * pos.reversed )
        return pos

    def __iadd__( self, distance ):
        self.set_position( self.tile, self.progress + distance * self.reversed )
        return self

    def __sub__( self, distance ):
        pos = copy.copy( self )
        pos.set_position( pos.tile, pos.progress - distance * pos.reversed )
        return pos

    def __isub__( self, distance ):
        self.set_position( self.tile, self.progress - distance * self.reversed )
        return self

    def __eq__( self, other ):
        return self.tile == other.tile and self.progress == other.progress

    def __ne__( self, other ):
        return not ( self == other )

    def to_next_tile( self ):
        old_tile = self.tile

        if self.reversed > 0:
            self.tile = self.tile.get_out_tile()
            if self.tile is None:
                self.tile = old_tile
                self.reverse_progress()
            elif self.tile.get_out_tile() == old_tile:
                self.reverse_progress()

        else:
            self.tile = self.tile.get_in_tile()
            if self.tile is None:
                self.tile = old_tile
                self.reverse_progress()
            elif self.tile.get_in_tile() == old_tile:
                self.reverse_progress()

        self.progress = 0;

    def get_out_direction( self ):
        """Return the current out direction of this position
        """
        if self.reversed > 0:
            return self.tile.trail.get_out_direction()
        else:
            return self.tile.trail.get_in_direction()

    def get_in_direction( self ):
        """Return the current in direction of this position
        """
        if self.reversed > 0:
            return self.tile.trail.get_in_direction()
        else:
            return self.tile.trail.get_out_direction()

    def get_screen_position( self ):
        """Returns tuple (x,y) of the position"""
        return self.tile.get_screen_position( self.progress )

    def get_distance( self, trailpos ):
        if self.tile == trailpos.tile:
            return abs( self.progress - trailpos.progress )

        elif self.tile.get_in_tile() == trailpos.tile:
            dist = self.progress

            if trailpos.tile.get_in_tile() == self.tile:
                return dist + trailpos.progress
            elif trailpos.tile.get_out_tile() == self.tile:
                return dist + trailpos.tile.get_length() - trailpos.progress

        elif self.tile.get_out_tile() == trailpos.tile:
            dist = self.tile.get_length() - self.progress

            if trailpos.tile.get_in_tile() == self.tile:
                return dist + trailpos.progress
            elif trailpos.tile.get_out_tile() == self.tile:
                return dist + trailpos.tile.get_length() - trailpos.progress
        return 999999999

    def same_direction( self, trailpos ):
        """Returns true if self and trailpos have same direction"""
        if self.tile == trailpos.tile:
            return self.reversed == trailpos.reversed

        elif self.tile.get_in_tile() == trailpos.tile:
            if trailpos.tile.get_in_tile() == self.tile:
                return self.reversed <> trailpos.reversed
            elif trailpos.tile.get_out_tile() == self.tile:
                return self.reversed == trailpos.reversed

        elif self.tile.get_out_tile() == trailpos.tile:
            if trailpos.tile.get_in_tile() == self.tile:
                return self.reversed == trailpos.reversed
            elif trailpos.tile.get_out_tile() == self.tile:
                return self.reversed <> trailpos.reversed


class TrailNode:
    """A node used for searching in trail (pathfinding etc)

    Properties:
    - tile: the tile where this node is at
    - in_dir: the direction where we came from
    - distance: the total distance to the first created node
    """
    def __init__( self, tile, in_dir ):
        """Create a Trailnode from a tile and in direction."""
        assert tile is not None

        self.tile = tile
        self.in_dir = in_dir
        self.distance = 0

##    # We don't need this anymore
##    def get_next_node( self ):
##        if self.in_dir is None or self.in_dir == self.tile.trail.get_in_direction():
##            node = TrailNode( self.tile.get_out_tile(), None )
##            out_dir = self.tile.trail.get_out_direction()
##        else:
##            node = TrailNode( self.tile.get_in_tile(), None )
##            out_dir = self.tile.trail.get_in_direction()
##
##        node.in_dir = out_dir.get_opposite()
##        node.distance = self.distance + 1
##        return node

    def get_out_nodes( self ):
        """Return a list of possible out nodes coming from this node."""
        nodes = []

        if isinstance(self.tile, Enterance):
            if self.in_dir in [Direction.NORTH, Direction.EAST]:
                pass # Just continue as a flat tile
            else:
                assert self.in_dir is not None, "We need a direction"

                for portal in self.tile.get_portals():
                    node = TrailNode( portal, self.in_dir.get_opposite() )
                    node.distance = self.distance + 1
                    nodes.append( node )
                return nodes

        if self.tile.type == Tile.Type.FLAT:
            for direction in Direction.ALL:
                if self.in_dir is None or direction <> self.in_dir:
                    neighbor = self.tile.get_neighbor( direction )
                    if neighbor is not None:
                        node = TrailNode( neighbor, direction.get_opposite() )
                        node.distance = self.distance + 1
                        nodes.append( node )

        else: # tile is hill
            node = TrailNode( self.tile.get_in_tile(), \
                             self.tile.trail.get_in_direction().get_opposite() )
            node.distance = self.distance + 1
            nodes.append( node )
        return nodes


class PathTree:
    """A tree that contains all path possibilities up to a certain generation.
    """
    def __init__( self ):
        """ """
        pass

    def move_root_to_node( self  ):
        """Set a new root node, and reuse as much of the existing tree as possible."""
        pass

    def update_to_generation( self, generation, max_proc_nodes = None):
        """Update the tree to include all paths up to a certain generation.

        You can also specify the maximum of nodes that may be processed at this
        time. The function returns True if all nodes up to the specified
        generation are calculated.
        """
        return False


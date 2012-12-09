
import struct
import random

import pygame
from pygame.locals import *
import copy

from tiles import Direction, Tile, TrailPosition, Enterance
from player import *
from pickups import *
from event import *

def tilesort( tile1, tile2 ):
    pos1 = -tile1.pos.x + tile1.pos.y
    pos2 = -tile2.pos.x + tile2.pos.y

    if pos1 < pos2:
        return -1
    elif pos1 > pos2:
        return 1
    else:
        return 0

class Level:
    """Board or map that contains the tiles and props."""
    def __init__( self ):
        self.tiles = []

    def set_tile( self, tile ):
        self.remove_tile( tile.pos.x, tile.pos.y )
        self.tiles.append( tile )

        self.tiles.sort( tilesort )

        self.update_neighbors();
        self.align_trails();

    def get_tile( self, x, y ):
        for tile in self.tiles:
            if tile.pos.x == x and tile.pos.y == y:
                return tile

        return None

    def remove_tile( self, x, y ):
        for tile in self.tiles:
            if tile.pos.x == x and tile.pos.y == y:
                self.tiles.remove( tile )
                self.update_neighbors()
                self.align_trails()
                return

    def update_neighbors( self ):
        for tile in self.tiles:
            self.update_tile_neighbors( tile )

        self.update_portals()

    def update_tile_neighbors( self, tile ):
        if tile is None: return

        for direction in Direction.ALL:
            offset = tile.get_neighbor_offset( direction )
            neighbor = None
            if offset.x <> 0 or offset.y <> 0:
                neighbor = self.get_tile( tile.pos.x + offset.x, tile.pos.y + offset.y )
                if neighbor is not None:
                    # only a neighbor if both connect with each other
                    if (offset * -1) <> neighbor.get_neighbor_offset( direction.get_opposite() ):
                        neighbor = None

            tile.set_neighbor( neighbor, direction )

    def update_portals( self ):
        portals = []
        for tile in self.tiles:
            if isinstance( tile, Enterance ):
                portals.append( tile )

        for portal in portals:
            others = portals[:]
            others.remove( portal )
            portal.set_portals( others )

    def align_trails( self ):
        for tile in self.tiles:
            tile.trail.align()

    def get_filename( nr ):
        return "data/levels/level%03d.lvl" % nr
    get_filename = staticmethod( get_filename )

    def save( self, filename ):
        f = open( filename, "wb" )

        data = struct.pack( "<i", len( self.tiles ) )
        f.write( data )

        for tile in self.tiles:
            tile.save( f )
        f.close()

    def load( self, filename ):
        f = open( filename, "rb" )

        data = f.read( struct.calcsize("<i") )
        data = struct.unpack( "<i", data )
        self.tiles = []
        for i in range(0, data[0]):
            self.tiles.append( Tile.load( f ) )

        f.close()

        self.update_neighbors()

    def get_first_flat_tile( self ):
        for tile in self.tiles:
            if tile.type == Tile.Type.FLAT and not isinstance(tile, Enterance):
                return tile
        return None

    def get_random_flat_tile( self ):
        flat_tiles = []
        for tile in self.tiles:
            if tile.type == Tile.Type.FLAT and not isinstance(tile, Enterance):
                flat_tiles.append( tile )

        return flat_tiles[ random.randint( 0, len(flat_tiles)-1 ) ]

    def get_first_portal( self ):
        portals = []
        for tile in self.tiles:
            if isinstance( tile, Enterance ):
                return tile

    def get_random_portal( self ):
        portals = []
        for tile in self.tiles:
            if isinstance( tile, Enterance ):
                portals.append( tile )

        return portals[ random.randint( 0, len(portals)-1 ) ]


class Playfield:
    """Contains all related to the playing area

    Public members:
    - level
    - goldcars
    """
    instance = None

    def __init__( self ):
        Playfield.instance = self
        self.level = Level()
        self.goldcars = []
        self.pickup_count = {}
        self.explosion = None

        self.dark_counter = None

        self.mirrors = []

    def load( self, level_filename ):
        self.level.load(level_filename)


    def add_goldcars( self, goldcar_names ):
        """Add goldcar with goldcar_names to this playfield

        goldcar_names - list of goldcar names
        """
        for name in goldcar_names:
            self.goldcars.append( GoldCar( None, len( self.goldcars ) ) )
            self.goldcars[ -1 ].name = name

    def get_goldcar_ranking( self ):
        """Return a sorted list of goldcars with same score"""
        single_ranking = self.goldcars[:]
        single_ranking.sort( lambda a, b: cmp( b.score, a.score ) )

        ranking = []
        prev_score = None
        for goldcar in single_ranking:
            if prev_score is not None and goldcar.score == prev_score:
                ranking[-1].append(goldcar)
            else:
                ranking.append([goldcar])
                prev_score = goldcar.score

        return ranking

    def spawn_next_goldcar( self, random_spawn = True ):
        """Returns False if all goldcars are on playfield"""
        for goldcar in self.goldcars:
            if goldcar.pos is None:
                if random_spawn:
                    goldcar.pos = TrailPosition( self.level.get_random_portal(), 0 )
                else:
                    goldcar.pos = TrailPosition( self.level.get_first_portal(), 0 )
                return True

        return False

    def game_tick( self ):
        self.pickup_count = {}


        for goldcar in self.goldcars:
            if goldcar.pos is not None: # for portal
                was_reversed = goldcar.pos.is_reversed()
                old_tile = goldcar.pos.tile

            goldcar.game_tick()

            if goldcar.pos is not None:
                # handle portal
                if isinstance( goldcar.pos.tile, Enterance ):
                    if was_reversed is not goldcar.pos.is_reversed() and\
                       old_tile is goldcar.pos.tile:
                        # collect pickups
                        if isinstance(goldcar.collectible, RockBlock):
                            goldcar.collectible = None
                            Event.rock_drop()
                        elif isinstance(goldcar.collectible, Diamond):
                            goldcar.collectible = None
                            goldcar.score += 10
                            Event.collect( 10, goldcar.pos )

                        # set new position
                        port = goldcar.pos.tile.get_random_portal()
                        new_pos = TrailPosition( port, 0.0 )

                        if self.is_free_position( new_pos, goldcar ):
                            goldcar.pos.tile = port
                            goldcar.pos.progress = 0.0

                self.handle_new_pickups( goldcar )
                self.handle_collisions( goldcar )
                goldcar.align_switch()
                self.handle_special_car_pickups( goldcar )


        for tile in self.level.tiles:
            tile.game_tick()

            if tile.pickup is not None:
                if isinstance( tile.pickup, Dynamite ):
                    if tile.pickup.explode():
                        tile.pickup = None

        # count total pickups
        for goldcar in self.goldcars:
                self.count_car_pickups( goldcar )
        for tile in self.level.tiles:
            if tile.pickup is not None:
                self.add_pickup_count( tile.pickup.__class__ )


        if self.explosion is not None:
            self.explosion.game_tick()

        if self.dark_counter is not None:
            old_counter = self.dark_counter
            self.dark_counter += 15

            if old_counter < 256 and self.dark_counter >= 256:
                # Reorder goldcars
                for goldcar in self.goldcars:
                    if goldcar.pos is not None:
                        new_pos = None
                        while new_pos is None: new_pos = self.get_free_position()
                        goldcar.clear_switch_and_pos()
                        goldcar.pos = new_pos
                        goldcar.select_next_switch()

            if self.dark_counter >= 256*2:
                self.dark_counter = None

        new_mirrors = []
        for mirror in self.mirrors:
            if mirror.is_done():
                self.goldcars.remove( mirror.twin )
            else:
                new_mirrors.append( mirror )
        self.mirrors = new_mirrors

    def handle_new_pickups( self, goldcar ):
        """Handle new tile pickups for goldcar"""
        if goldcar.pos.tile.pickup is not None:
            pickup = goldcar.pos.tile.pickup

            if isinstance( goldcar.collectible, RockBlock ):
                pass #don't pickup anything else!

            elif isinstance( goldcar.collectible, Diamond ) and \
                   isinstance( pickup, Diamond):
                pass #don't pickup if I already got one

            elif isinstance(pickup, GoldBlock):
                if isinstance( goldcar.collectible, Axe ):
                    goldcar.add_pickup( goldcar.pos.tile.pickup )
                    goldcar.pos.tile.pickup = None

            elif isinstance(pickup, Flag):
                if goldcar is pickup.goldcar:
                    goldcar.add_pickup( goldcar.pos.tile.pickup )
                    goldcar.pos.tile.pickup = None

            elif isinstance(pickup, Torch):
                if self.dark_counter is None:
                    goldcar.pos.tile.pickup = None
                    self.dark_counter = 0

            elif isinstance(goldcar.collectible, Dynamite) and \
                 isinstance(pickup, PowerUp):
                pass # don't pickup PowerUp!

            elif isinstance( pickup, PowerUp ) \
                 and isinstance( goldcar.collectible, Collectible ):
                pass # don't pickup PowerUp when we have collectible

            else:
                goldcar.add_pickup( goldcar.pos.tile.pickup )
                goldcar.pos.tile.pickup = None

            if isinstance( pickup, Mirror ):
                twin = GoldCar( self.get_free_position(), goldcar.nr )
                pickup.set_twin( twin )
                self.goldcars.append( twin )
                twin.name = ""

                self.mirrors.append( pickup )

    def handle_collisions( self, goldcar ):
        """Handle collisions n stuff"""
        for car2 in self.goldcars:
            if goldcar is not car2 and car2.pos is not None:
                goldcar.handle_collision( car2 )

                # only closest car has power on switch
                if goldcar.switch == car2.switch and goldcar.switch is not None:
                    if goldcar.switch_dist < car2.switch_dist:
                        car2.switch = None
                    else:
                        goldcar.switch = None

    def count_car_pickups( self, goldcar ):
        if goldcar.modifier is not None:
            self.add_pickup_count( goldcar.modifier.__class__ )

        if goldcar.collectible is not None:
            self.add_pickup_count( goldcar.collectible.__class__ )

    def handle_special_car_pickups( self, goldcar ):
        if isinstance( goldcar.collectible, Key ):
            self.add_pickup_count( Key )
            if goldcar.key_went_down():
                for tile in self.level.tiles:
                    if tile.is_switch() and \
                               goldcar.switch <> tile:
                        tile.switch_it()
        if isinstance( goldcar.modifier, Ghost ):
            if goldcar.modifier.is_done() \
               and self.is_free_position( goldcar.pos, goldcar ):
                goldcar.modifier = None

    def get_pickup_count( self, pickup_class ):
        """Return the number of pickups in the entire play."""
        if self.pickup_count.has_key( pickup_class ):
            return self.pickup_count[pickup_class]
        else:
            return 0

    def add_pickup_count( self, pickup_class, increment = 1 ):
        """Increment the pickup count"""
        if self.pickup_count.has_key( pickup_class ):
            self.pickup_count[pickup_class] += increment
        else:
            self.pickup_count[pickup_class] = increment

    def spawn_dynamite_on_car( self, goldcar ):
        if goldcar.collectible is None:
            goldcar.add_pickup( Dynamite() )

    def spawn_pickup( self, pickup ):
        """Spawn the pickup at a random location, or no location at all, and
        return the tile location."""
        tile = self.level.get_random_flat_tile()
        if tile.pickup is None:
            tile.pickup = pickup
            x, y = tile.get_center()
            tile.pickup.container = tile
            return tile
        return None

    def get_free_position( self ):
        """Return a random free position, or None if not quickly found"""
        tile = self.level.get_random_flat_tile()
        if tile.pickup is None:
            pos = TrailPosition(tile, tile.get_length() / 2)
            if self.is_free_position( pos ):
                return pos
        return None

    def is_free_position( self, position, ignore = None ):
        """Return true if the position is free"""
        for goldcar in self.goldcars:
            if goldcar.pos is not None:
                distance = goldcar.pos.get_distance( position )
                if distance < (GoldCar.COLLIDE_DISTANCE * 1.2) and goldcar is not ignore:
                    return False

        return True



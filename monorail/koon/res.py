#!/usr/bin/env python
"""use 'resman' as the main ResourceManager in this module
"""
import pygame

import geo
import cfg
import gfx
import snd

class ResourceManager:
    def __init__( self ):
        self.loaded_files = {}
        self.loaded_resources = {}

    def read( self, filename ):
        """Read in the resource file."""
        conf_file = cfg.ConfigFile(filename)
        self.root_node = conf_file.root_node

    def get( self, res_name, typ = str ):
        """Returns the resource

        Supports following types: str, int, pygame.Rect
        """
        if res_name not in self.loaded_resources:
            node = self.root_node.get(res_name)
            self.loaded_resources[ res_name ] = self.get_from_node( node, typ )

        return self.loaded_resources[ res_name ]

    def get_from_node( self, node, typ = str ):
        # Simple type
        if len(node.attribs) == 0:
            if typ is None or typ is str:
                return node.value
            elif typ is int:
                return int(node.value)

        # Complex type
        else:
            if node.value == "Rectangle":
                return pygame.Rect(
                    int( node.get("x").value ),
                    int( node.get("y").value ),
                    int( node.get("width").value ),
                    int( node.get("height").value ) )
                
            elif node.value == "Vec2D":
                return geo.Vec2D(
                    typ( node.get("x").value ),
                    typ( node.get("y").value ) )

            elif node.value == "Surface":
                return gfx.Surface( node.get("file").value )

            elif node.value == "SpriteFilm":
                sprite = gfx.SpriteFilm( self.get( node.get("surface").value ) )
                sprite.set_div( int( node.get("div_x").value ),
                                int( node.get("div_y").value ) )
                sprite.center = geo.Vec2D( int( node.get("center_x").value ),
                                           int( node.get("center_y").value ) )
                return sprite

            elif node.value == "SubSurf":
                if "surface" in node.attribs.keys():
                    subsurf = gfx.SubSurf( self.get( node.get("surface").value ) )
                    subsurf.rect = self.get_from_node( node.get("rect") )
                else:
                    subsurf = gfx.SubSurf( gfx.Surface( node.get("file").value ) )
                    
                if "offset_x" in node.attribs.keys():
                    subsurf.offset = geo.Vec2D(
                            int( node.get("offset_x").value),
                            int( node.get("offset_y").value) )
                return subsurf

            elif node.value == "Music":
                return snd.Music( node.get("file").value )
                
            elif node.value == "Sound":
                return snd.Sound( node.get("file").value )
                
            else:
                raise Exception("unknown type in resource file")
        
    
    def load( self, filename ):
        """Load a file, or get it from memory."""
        if filename not in self.loaded_files:
            if filename.lower().endswith(".png") or filename.lower().endswith(".jpg"):
                self.loaded_files[ filename ] = pygame.image.load( filename ).convert_alpha()
                
        return self.loaded_files[ filename ]


resman = ResourceManager()

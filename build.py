#!/usr/bin/env python2

import os
from os import path

from PIL import Image, ImageSequence

import monorail.koon.build as build
import monorail.koon.cfg as cfg

print "Updating data from assets..."

CONFIGFILE = "data/800x600/resources.cfg"

cf = cfg.ConfigFile( CONFIGFILE )


node = build.generate_sprite("dynamite_sprite", "data/800x600/gfx/dynamite.png",
                     "assets/3d/dynamite.blend", 0.12, 4, center=(46, 216))
cf.root_node.get("game").append_attribute( node )

TILESCALE = 64.0/266.0
TILEOFFSET = (258,179)
PICKUPOFFSET = (389,273)

#
node = build.generate_sprite("tile0_surf", "data/800x600/gfx/tileflat.png",
                     "assets/3d/tiles.blend", TILESCALE, 5, scene="TileFlat",
                     center=TILEOFFSET)
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite("", "data/800x600/gfx/tilehill.png",
                     "assets/3d/tiles.blend", TILESCALE, 4, scene="TileHill",
                     center=TILEOFFSET)

if node is not None:    
    width = int(node.get("frame_width").value)
    height = int(node.get("frame_height").value)
    center_x = int(node.get("center_x").value)
    center_y = int(node.get("center_y").value)

    r_x = 2 * width + center_x + 16
    r_y = 0
    r_width = width - (center_x + 16)
    r_height = height
    
    cf.root_node.set("game.tile1_surf.offset_x", - 16)
    cf.root_node.set("game.tile1_surf.offset_y", center_y)
    cf.root_node.set("game.tile1_surf.rect.x", r_x)
    cf.root_node.set("game.tile1_surf.rect.y", r_y)
    cf.root_node.set("game.tile1_surf.rect.width", r_width)
    cf.root_node.set("game.tile1_surf.rect.height", r_height)
    cf.root_node.set("game.tile1_surf.surface", "game.tilehill_surf")

    r_x = 2 * width
    r_width = center_x + 16

    cf.root_node.set("game.tile2_surf.offset_x", center_x - 32)
    cf.root_node.set("game.tile2_surf.offset_y", center_y + 16)
    cf.root_node.set("game.tile2_surf.rect.x", r_x)
    cf.root_node.set("game.tile2_surf.rect.y", r_y)
    cf.root_node.set("game.tile2_surf.rect.width", r_width)
    cf.root_node.set("game.tile2_surf.rect.height", r_height)
    cf.root_node.set("game.tile2_surf.surface", "game.tilehill_surf")

    r_x = 3 * width
    r_width = center_x + 48

    cf.root_node.set("game.tile3_surf.offset_x", center_x)
    cf.root_node.set("game.tile3_surf.offset_y", center_y)
    cf.root_node.set("game.tile3_surf.rect.x", r_x)
    cf.root_node.set("game.tile3_surf.rect.y", r_y)
    cf.root_node.set("game.tile3_surf.rect.width", r_width)
    cf.root_node.set("game.tile3_surf.rect.height", r_height)
    cf.root_node.set("game.tile3_surf.surface", "game.tilehill_surf")

    r_x = 3 * width + center_x + 48
    r_width = width - (center_x + 48)

    cf.root_node.set("game.tile4_surf.offset_x", -16)
    cf.root_node.set("game.tile4_surf.offset_y", center_y + 16)
    cf.root_node.set("game.tile4_surf.rect.x", r_x)
    cf.root_node.set("game.tile4_surf.rect.y", r_y)
    cf.root_node.set("game.tile4_surf.rect.width", r_width)
    cf.root_node.set("game.tile4_surf.rect.height", r_height)
    cf.root_node.set("game.tile4_surf.surface", "game.tilehill_surf")

    r_x = 0 * width 
    r_width = center_x + 48

    cf.root_node.set("game.tile5_surf.offset_x", center_x)
    cf.root_node.set("game.tile5_surf.offset_y", center_y)
    cf.root_node.set("game.tile5_surf.rect.x", r_x)
    cf.root_node.set("game.tile5_surf.rect.y", r_y)
    cf.root_node.set("game.tile5_surf.rect.width", r_width)
    cf.root_node.set("game.tile5_surf.rect.height", r_height)
    cf.root_node.set("game.tile5_surf.surface", "game.tilehill_surf")

    r_x = 0 * width + center_x + 48
    r_width = width - (center_x + 48)

    cf.root_node.set("game.tile6_surf.offset_x", -16)
    cf.root_node.set("game.tile6_surf.offset_y", center_y + 48)
    cf.root_node.set("game.tile6_surf.rect.x", r_x)
    cf.root_node.set("game.tile6_surf.rect.y", r_y)
    cf.root_node.set("game.tile6_surf.rect.width", r_width)
    cf.root_node.set("game.tile6_surf.rect.height", r_height)
    cf.root_node.set("game.tile6_surf.surface", "game.tilehill_surf")

    r_x = 1 * width + center_x + 16
    r_y = 0
    r_width = width - (center_x + 16)
    r_height = height
    
    cf.root_node.set("game.tile7_surf.offset_x", - 16)
    cf.root_node.set("game.tile7_surf.offset_y", center_y)
    cf.root_node.set("game.tile7_surf.rect.x", r_x)
    cf.root_node.set("game.tile7_surf.rect.y", r_y)
    cf.root_node.set("game.tile7_surf.rect.width", r_width)
    cf.root_node.set("game.tile7_surf.rect.height", r_height)
    cf.root_node.set("game.tile7_surf.surface", "game.tilehill_surf")

    r_x = 1 * width
    r_width = center_x + 16

    cf.root_node.set("game.tile8_surf.offset_x", center_x - 32)
    cf.root_node.set("game.tile8_surf.offset_y", center_y + 48)
    cf.root_node.set("game.tile8_surf.rect.x", r_x)
    cf.root_node.set("game.tile8_surf.rect.y", r_y)
    cf.root_node.set("game.tile8_surf.rect.width", r_width)
    cf.root_node.set("game.tile8_surf.rect.height", r_height)
    cf.root_node.set("game.tile8_surf.surface", "game.tilehill_surf")


#
node = build.generate_image("exitbot_surf", "data/800x600/gfx/exitbot.png",
                     "assets/3d/tiles.blend", scale=TILESCALE, scene="exitBot",
                     offset=TILEOFFSET)
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_image("exittop_surf", "data/800x600/gfx/exittop.png",
                     "assets/3d/tiles.blend", scale=TILESCALE, scene="exitTop",
                     offset=TILEOFFSET)
cf.root_node.get("game").append_attribute( node )



#
##node = build.generate_sprite("data/800x600/gfx/railgate.png",
##                     "assets/3d/tiles.blend", scale=TILESCALE, count=12,
##                      scene="railgate", center=TILEOFFSET)

for i in range(1, 7):
    node = build.generate_sprite( "car%d_sprite"%i, "data/800x600/gfx/car%d.png"%i,
                           "assets/3d/car.blend", 0.25, 80,
                           "Car%d"%i, (391, 311) )
    cf.root_node.get("game").append_attribute( node )

    #
    node = build.generate_sprite( "flag%d_sprite"%i, "data/800x600/gfx/flag%d.png"%i,
                                    "assets/3d/flag.blend",
                                    TILESCALE, 8, scene="flag%d"%i,center = PICKUPOFFSET )
    cf.root_node.get("game").append_attribute( node )


#
build.generate_sprite( "", "data/800x600/gfx/oil.png",
                       "assets/3d/oil.blend", 0.4, 5 )

#
build.generate_sprite( "", "data/800x600/gfx/diamond.png",
                       "assets/3d/diamond.blend", 0.18, 4 )

#
node = build.generate_sprite( "copper_sprite", "data/800x600/gfx/copper.png",
                                "assets/3d/copper.blend",
                                0.08, 9, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite( "rock_sprite", "data/800x600/gfx/rock.png",
                                "assets/3d/rock.blend",
                                0.25, 16, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite( "axe_sprite", "data/800x600/gfx/pickaxe.png",
                                "assets/3d/pickaxe.blend",
                                0.12, 9, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

node = build.generate_sprite( "lamp_sprite", "data/800x600/gfx/lamp.png",
                                "assets/3d/lamp.blend",
                                0.13, 1, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

node = build.generate_sprite( "balloon_sprite", "data/800x600/gfx/balloon.png",
                                "assets/3d/balloon.blend",
                                0.13, 1, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

node = build.generate_sprite( "ghost_sprite", "data/800x600/gfx/ghost.png",
                                "assets/3d/ghost.blend",
                                0.22, 1, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

node = build.generate_sprite( "torch_sprite", "data/800x600/gfx/torch.png",
                                "assets/3d/torch.blend",
                                0.18, 1, center = PICKUPOFFSET )
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite( "key_sprite", "data/800x600/gfx/key.png",
                                "assets/3d/key.blend",
                                0.35, 19, center = PICKUPOFFSET )

cf.root_node.get("game").append_attribute( node )

#
#node = build.generate_sprite( "mirror_sprite", "data/800x600/gfx/mirror.png",
#                                "assets/3d/mirror.blend",
#                                0.20, 9, center = PICKUPOFFSET )
#cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite( "explosion_sprite", "data/800x600/gfx/explosion.png",
                                "assets/3d/explosion.blend",
                                0.4, 16, center = (296,228) )
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_sprite( "introcar_sprite", "data/800x600/gfx/introcar.png",
                                "assets/3d/intro.blend",
                                1.0, 5, center = (0,0), scene="rails" )
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("introcar_car", "data/800x600/gfx/introcar_car.png",
                     "assets/3d/intro.blend", scale=1.0, offset=(0,0), scene="car")
if node is not None: node.value = "SubSurf"
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("introcar_man", "data/800x600/gfx/introcar_man.png",
                     "assets/3d/intro.blend", scale=1.0, offset=(0,0), scene="man")
if node is not None: node.value = "SubSurf"
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("introcar_hat", "data/800x600/gfx/introcar_hat.png",
                     "assets/3d/intro.blend", scale=1.0, offset=(0,0), scene="hat")
if node is not None: node.value = "SubSurf"
cf.root_node.get("game").append_attribute( node )

#
node = build.generate_image("paperdialog_surf", "data/800x600/gfx/paperdialog.png",
                     "assets/3d/dialog.blend", scale=1, offset=(0,0))
#cf.root_node.get("game").append_attribute( node )


#
node = build.generate_image("", "data/800x600/gfx/levelselect3d.png",
                     "assets/3d/levelselect.blend", scale=1,
                      scene="Scene",offset=(0, 0))

#
node = build.generate_image("", "data/800x600/gfx/congrats.png",
                     "assets/3d/levelselect.blend", scale=1,
                      scene="congrats",offset=(0, 0))

#
node = build.generate_sprite("", "data/800x600/gfx/levelpoint.png",
                     "assets/3d/levelselect.blend", scale=0.125, count=5,
                      scene="bullet", center=(149, 148))


#
node = build.generate_sprite( "sheriffstar_sprite", "data/800x600/gfx/sheriffstar.png",
                                "assets/3d/sheriffstar.blend",
                                0.5, 3, center = (202,126) )
cf.root_node.get("gui").append_attribute( node )

#
node = build.generate_sprite( "crate_sprite", "data/800x600/gfx/crate.png",
                                "assets/3d/crate.blend",
                                0.185, 12, center = (292,184) )
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("crate_label_surf", "data/800x600/gfx/crate_label.png",
                     "assets/3d/cratelabel.blend", scale=0.185)
cf.root_node.get("game").append_attribute( node )


node = build.generate_image("hud_score_surf", "data/800x600/gfx/hud_score.png",
                     "assets/3d/hud_score.blend", scale=0.65)
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("hud_watch_surf", "data/800x600/gfx/hud_watch.png",
                     "assets/3d/watch.blend", scale=0.35)
cf.root_node.get("game").append_attribute( node )


node = build.generate_image("skill_bar_surf", "data/800x600/gfx/skill_bar.png",
                     "assets/3d/skill_bar.blend", offset=(422, 293),scale=0.37, scene="bar")
if node is not None: node.value = "SubSurf"
cf.root_node.get("game").append_attribute( node )

node = build.generate_image("skill_pointer_surf", "data/800x600/gfx/skill_pointer.png",
                     "assets/3d/skill_bar.blend", offset=(422, 293),scale=0.37, scene="pointer")
if node is not None: node.value = "SubSurf"
cf.root_node.get("game").append_attribute( node )


cf.save( CONFIGFILE )

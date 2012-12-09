
import os
from os import path

from PIL import Image, ImageSequence

import monorail.koon.cfg as cfg


# TODO: make first one also list
def should_update( filename, filenames_list ):
    """returns True if filename is older than the newest in filenames_list"""
    if not os.path.exists( filename ):
        return True
    time = os.path.getmtime( filename )
    for f in filenames_list:
        if time < os.path.getmtime( f ):
            return True
    return False


def get_bounding_box( image ):
    x, y = 0, 0
    box = [ None, None, None, None ]
    for color in image.getdata():
        if len(color) <= 3 or color[3] != 0:
            if box[0] is None: box[0] = x
            else:              box[0] = min((box[0], x))
            if box[1] is None: box[1] = y
            else:              box[1] = min((box[1], y))
            if box[2] is None: box[2] = x
            else:              box[2] = max((box[2], x))
            if box[3] is None: box[3] = y
            else:              box[3] = max((box[3], y))

        x += 1
        if x == image.size[0]:
            y += 1
            x = 0
    if box[0] is not None:
        return box
    else:
        return None

def max_bounding_box( images ):
    box = [ 999999999, 99999999999, -1, -1 ]
    for im in images:
        b = get_bounding_box( im )
        if b is not None:
            box[0] = min( b[0], box[0] )
            box[1] = min( b[1], box[1] )
            box[2] = max( b[2], box[2] )
            box[3] = max( b[3], box[3] )
    return box

def pack_images( images ):
    """Returns the packed images (all of same size)"""
    width = images[0].size[0]
    height = images[0].size[1]


    out_width = min([len(images), 10]) * width
    out_height = ((len(images)-1) / 10 + 1) * height

    out_image = Image.new("RGBA", (out_width,out_height))

    x = 0
    y = 0
    for im in images:
        out_image.paste( im, (x*width, y*height) )
        x += 1
        if x == 10:
            y += 1
            x = 0
    return out_image


def generate_sprite( configname, spritefilename, blenderfilename, scale, count,
                     scene = None, center = None ):
    node = cfg.ConfigNode( configname )
    node.value = "SpriteFilm"

    tmpfilename = "assets/tmp/" + path.basename(spritefilename)
    tmpfilename = tmpfilename.replace(".", "_%04d.")

    if should_update( tmpfilename % 1, [blenderfilename] ):
        for i in range(1, count+1):
            print "generating", tmpfilename % i
            outname = tmpfilename[ 0: tmpfilename.rfind("_") ]
            if scene is None:
                os.system( "blender -b "+blenderfilename+" -F PNG -o "+outname+"_ -f "+str(i) )
            else:
                os.system( "blender -b "+blenderfilename+" -S "+scene+" -F PNG -o "+outname+"_ -f "+str(i) )

    if should_update( spritefilename, [tmpfilename % i for i in range(1,count+1)] ):
        print "generating sprite", spritefilename

        filenames = [tmpfilename % i for i in range(1,count+1)]
        images = [Image.open(filename) for filename in filenames]

        images = [im.resize( (int(im.size[0]*scale), int(im.size[1]*scale)), Image.ANTIALIAS ) for im in images]

        box = max_bounding_box( images )

        if center is not None:
            node.set("center_x", int(round(center[0] * scale - box[0])))
            node.set("center_y", int(round(center[1] * scale - box[1])))
        node.set("frame_width", int(box[2] - box[0]))
        node.set("frame_height", int(box[3] - box[1]))
        node.set("div_x", min(len(images), 10) )
        node.set("div_y", (len(images) / 10) + 1)

        images = [im.crop( box ) for im in images]
        for im in images:
            im.load() # for lazy crop

        out_image = pack_images( images )
        out_image.save(spritefilename)

        return node

def generate_image( configname, imagefilename, blenderfilename, scale,
                    scene = None, offset = None ):
    node = cfg.ConfigNode( configname )
    node.value = "Surface"
#    node.set( "file", imagefilename )

    tmpfilename = "assets/tmp/" + path.basename(imagefilename)
    tmpfilename = tmpfilename.replace(".", "_0001.")

    if should_update( tmpfilename, [blenderfilename] ):
        print "generating", tmpfilename
        outfilename = tmpfilename[0: tmpfilename.rfind("_") ]
        if scene is None:
            os.system("blender -b "+blenderfilename+" -F PNG -o "+outfilename+"_ -f 1")
        else:
            os.system("blender -b "+blenderfilename+" -S "+scene+" -F PNG -o "+outfilename+"_ -f 1")


    if should_update(imagefilename, [tmpfilename] ):
        print "generating image", imagefilename
        im = Image.open(tmpfilename)

        im = im.resize( (int(im.size[0]*scale), int(im.size[1]*scale)), Image.ANTIALIAS )

        box = get_bounding_box( im )

        if offset is not None and box is not None:
            node.set("offset_x", int(round(offset[0] * scale - box[0])))
            node.set("offset_y", int(round(offset[1] * scale - box[1])))

        im = im.crop( box )
        im.load() # for lazy crop

        im.save(imagefilename)

        return node

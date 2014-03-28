#!/usr/bin/env python
import os
import sys
import png
import struct


def get_arguments():
    if len(sys.argv) < 2:
        print("No FNT file specified.")
        sys.exit(-1)
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Not a valid file \"{}\".".format(filename))
        sys.exit(-1)

    if len(sys.argv) < 3:
        print("No PAL file specified.")
        sys.exit(-1)
    palfile = sys.argv[2]
    if not os.path.isfile(palfile):
        print("Not a valid palette file \"{}\".".format(palfile))
        sys.exit(-1)
    palfile = open(palfile, 'rb')
    palette = read_palette(palfile)
    palfile.close()

    return os.path.abspath(filename), palette


def extract_characters(filename, pal):
        handle = open(filename, 'rb')
        magic = struct.unpack('<I', handle.read(4))[0]
        if magic != 0x00002e31:
            raise Exception("Invalid FNT file (bad signature).")

        character_count = struct.unpack('<I', handle.read(4))[0]
        character_height = struct.unpack('<I', handle.read(4))[0]
        color_transparent = struct.unpack('<I', handle.read(4))[0]
        pal[color_transparent][3] = 0x00  # set 'transparent' palette entry's opacity to zero

        dir, file_ = os.path.split(os.path.abspath(filename))
        dir = os.path.join(dir, file_.replace('.fnt', ''))
        if not os.path.isdir(dir):
            os.makedirs(dir)
        for i in range(character_count):
            off_char = struct.unpack('<I', handle.read(4))[0]
            off_restore = handle.tell()
            handle.seek(off_char)
            fnt_to_png(dir, pal, handle, i, character_height)
            handle.seek(off_restore)


def read_palette(handle, size=256):
    entries = []
    for index in range(size):
        rgb = handle.read(3)
        entries.append([rgb[0] << 2, rgb[1] << 2, rgb[2] << 2, 0xFF])
    return entries


def fnt_to_png(dir, palette, handle, entry, height):
    __, parent = os.path.split(dir)
    pngstr = "{:02X}.png".format(entry)
    filename = os.path.join(dir, pngstr)
    testname = os.path.join(parent, pngstr)

    width = struct.unpack('<I', handle.read(4))[0]
    if not width:
        return

    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            row += palette[handle.read(1)[0]]
        pixels.append(row)

    fout = open(filename, 'wb')
    w = png.Writer(width=width, height=height, bitdepth=8, alpha=True)
    w.write(fout, pixels)
    fout.close()


def main():
    filename, palette = get_arguments()
    extract_characters(filename, palette)


main()

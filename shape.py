#!/usr/bin/env python
import os
import sys
import png
import struct


def get_arguments():
    if len(sys.argv) < 2:
        print("No SHP file specified.")
        sys.exit(-1)
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Not a valid file \"{}\".".format(filename))
        sys.exit(-1)

    palette = None
    if len(sys.argv) == 3:
        palfile = sys.argv[2]
        if not os.path.isfile(palfile):
            print("Not a valid palette file \"{}\".".format(palfile))
            sys.exit(-1)
        palfile = open(palfile, 'rb')
        palette = read_palette(palfile)
        palfile.close()

    return os.path.abspath(filename), palette


def extract_shapes(filename, pal0):
        handle = open(filename, 'rb')
        magic = struct.unpack('<I', handle.read(4))[0]
        if magic != 0x30312E31:
            raise Exception("Invalid SHP file (bad signature).")
        image_count = struct.unpack('<I', handle.read(4))[0]
        dir, file_ = os.path.split(os.path.abspath(filename))
        dir = os.path.join(dir, file_.replace('.shp', ''))
        if not os.path.isdir(dir):
            os.makedirs(dir)
        for i in range(image_count):
            off_dat = struct.unpack('<I', handle.read(4))[0]
            off_pal = struct.unpack('<I', handle.read(4))[0]
            off_restore = handle.tell()

            palette = pal0
            if off_pal != 0:
                handle.seek(off_pal)
                palette = read_palette(handle)
            elif pal0 is None:
                print("Default palette required for {}/{}; skipping...".format(i+1, image_count))
                continue

            handle.seek(off_dat)
            shp_to_png(dir, palette, handle, i+1, image_count)
            handle.seek(off_restore)


def read_palette(handle, size=256):
    entries = []
    for index in range(size):
        rgb = handle.read(3)
        entries.append([rgb[0] << 2, rgb[1] << 2, rgb[2] << 2, 0xFF])
    return entries


def shp_to_png(dir, palette, handle, entry, total):
    __, parent = os.path.split(dir)
    idxlen = len("{}".format(total))
    pngstr = "{}".format(entry).rjust(idxlen, '0')
    pngstr = "".join([pngstr, '.png'])
    filename = os.path.join(dir, pngstr)
    testname = os.path.join(parent, pngstr)

    height = 1 + struct.unpack('<H', handle.read(2))[0]
    width = 1 + struct.unpack('<H', handle.read(2))[0]

    x_center = struct.unpack('<H', handle.read(2))[0]
    y_center = struct.unpack('<H', handle.read(2))[0]
    x_start  = struct.unpack('<i', handle.read(4))[0]
    y_start  = struct.unpack('<i', handle.read(4))[0]
    x_end    = struct.unpack('<i', handle.read(4))[0]
    y_end    = struct.unpack('<i', handle.read(4))[0]
    if (x_start > (width-1)) or (y_start > (width-1)):
        print("Unable to create {} (w:{}, h:{}, x:{}, y:{}).".format(testname, width, height, x_start, y_start))
        return

    top = y_center + y_start
    bottom = y_center + y_end
    left = x_center + x_start

    background = [0, 0, 0, 0xFF]
    pad_row = background * width
    pad_left = background * left

    y = 0
    row = []
    pixels = []

    # this doesn't seem right... but works
    plane_width = width << 2
    read_width = (x_center + x_end + (x_center + x_start)) << 2
    if plane_width > read_width: read_width = plane_width

    while y < height:
        if (y < top) or (y >= bottom):
            pixels.append(pad_row)
            y += 1
            continue

        if len(row) == 0:
            row += pad_left

        try:
            b = handle.read(1)[0]
        except Exception as e:
            print("Unable to create {} (hit EOF at {},{} of {},{}).".format(testname, len(row) >> 2, y, width, height))
            return

        if b == 0:
            # this doesn't seem right either...
            if len(row) == len(pad_left):
                continue
            row += background * ((read_width - len(row)) >> 2)
        elif b == 1:
            px = handle.read(1)[0]
            row += background * px
        elif (b & 1) == 0:
            clr = palette[handle.read(1)[0]]
            for i in range(b >> 1):
                row += clr
        else:
            for i in range(b >> 1):
                clr = palette[handle.read(1)[0]]
                row += clr

        if len(row) == read_width:
            row = row[:plane_width]
            pixels.append(row)
            row = []
            y += 1

    fout = open(filename, 'wb')
    w = png.Writer(width=width, height=height, bitdepth=8, alpha=True)
    w.write(fout, pixels)
    fout.close()


def main():
    filename, palette = get_arguments()
    extract_shapes(filename, palette)


main()

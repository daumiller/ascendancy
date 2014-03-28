#!/usr/bin/env python
import os
import sys
import wave
import struct


def get_arguments():
    if len(sys.argv) < 2:
        print("No VOC file specified.")
        sys.exit(-1)
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Not a valid file \"{}\".".format(filename))
        sys.exit(-1)
    return os.path.abspath(filename)


def convert_voice(filename):
        # http://wiki.multimedia.cx/index.php?title=Creative_Voice
        handle = open(filename, 'rb')
        try:
            magic_a = handle.read(19).decode('utf-8')
        except Exception:
            # turns out that _most_ of the VOC files are actually just raw PCM data...
            #print("Invalid VOC file (bad/no signature)({}).".format(filename), file=sys.stderr)
            # RAW PCM data at 22050 Hz, 8 bits, Mono
            handle.seek(0)
            dump_wave(filename, 22050, 1, handle.read())
            return

        magic_b = handle.read(1)[0]
        if (magic_a != "Creative Voice File") or (magic_b != 0x1A):
            #print("Invalid VOC file (bad signature)({}).".format(filename), file=sys.stderr)
            # RAW PCM data
            handle.seek(0)
            dump_wave(filename, 22050, 1, handle.read())
            return

        handle.read(2)  # header size, don't care...
        maj_min = struct.unpack('<H', handle.read(2))[0]
        ver_chk = struct.unpack('<H', handle.read(2))[0]
        if ver_chk != 0x1234 + ~maj_min:
            print("Invalid VOC File (bad version check)({}).".format(filename), file=sys.stderr)
            sys.exit(-1)

        while 1:
            block_type = 0
            try:
                block_type = handle.read(1)[0]
            except Exception:
                break
            if block_type == 0:
                break

            # check for our small implementation set (all valid Ascendancy VOCs use this configuration):
            # 8 bit unsigned, 22050 Hz, mono, Uncompressed -- OR
            # 8 bit unsigned, 11025 Hz, stereo, Uncompressed
            if block_type == 9:
                handle.seek(handle.tell()-1)
                size = struct.unpack('<I', handle.read(4))[0] >> 8
                sample_rate = struct.unpack('<I', handle.read(4))[0]
                sample_bits = handle.read(1)[0]
                channel_count = handle.read(1)[0]
                codec_id = struct.unpack('<H', handle.read(2))[0]
                handle.read(4)  # four reserved bytes
                if sample_bits != 8: raise Exception("Non-standard sample bits ({}).".format(sample_bits))
                if codec_id != 0: raise Exception("Non-standard codec id ({}).".format(codec_id))
                dump_wave(filename, sample_rate, channel_count, handle.read(size))
            else:
                raise Exception("Unimplemented block type {:02X}".format(block_type))


def dump_wave(filename, rate, channels, data):
    wav = wave.open(filename.replace('.voc', '.wav').replace('.raw', '.wav'), 'wb')
    wav.setsampwidth(1)
    wav.setnchannels(channels)
    wav.setframerate(rate)
    wav.writeframes(data)
    wav.close()


def main():
    filename = get_arguments()
    convert_voice(filename)


main()

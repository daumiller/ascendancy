#!/usr/bin/env python
import os
import io
import sys
import struct


def get_arguments():
    if len(sys.argv) < 2:
        print("No COB file specified.")
        sys.exit(-1)
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Not a valid file \"{}\".".format(filename))
        sys.exit(-1)
    filename = os.path.abspath(filename)

    dirname = None
    if len(sys.argv) == 3:
        dirname = sys.argv[2]
        if not os.path.isdir(dirname):
            print("Not a valid destination directory \"{}\".".format(dirname))
            sys.exit(-1)
        dirname = os.path.abspath(dirname)

    return filename, dirname


class cob_file():
    def __init__(self, dirname, filename):
        self.path = dirname
        self.name = filename
        self.size = 0
        self.offset = 0


class cob_archive():
    def __init__(self, filename):
        self._handle = open(filename, 'rb')
        self._handle.seek(0, io.SEEK_SET)
        self.files = []
        count = struct.unpack('<i', self._handle.read(4))[0]
        if count < 1: return
        for index in range(count):
            path = self._handle.read(50).partition(b'\0')[0].decode('utf-8')
            dirname, filename = os.path.split(path.replace('\\', '/'))
            self.files.append(cob_file(dirname, filename))
        self.files[0].offset = struct.unpack('<I', self._handle.read(4))[0]
        for index in range(1, count):
            self.files[index].offset = struct.unpack('<I', self._handle.read(4))[0]
            self.files[index-1].size = self.files[index].offset - self.files[index-1].offset
        self._handle.seek(0, io.SEEK_END)
        self.files[count-1].size = self._handle.tell() - self.files[count-1].offset

    def close(self):
        self._handle.close()

    def file_write(self, index, path):
        fout = open(path, 'wb')
        self._handle.seek(self.files[index].offset)
        fout.write(self._handle.read(self.files[index].size))
        fout.close()


def main():
    filename, dirname = get_arguments()
    cob = cob_archive(filename)

    if dirname is None:
        for i in range(len(cob.files)):
            print("{:3}:  {:10}  {}".format(i+1, cob.files[i].size, cob.files[i].name))
    else:
        for i in range(len(cob.files)):
            parent = os.path.join(dirname, cob.files[i].path)
            if not os.path.isdir(parent):
                os.makedirs(parent)
            cob.file_write(i, os.path.join(parent, cob.files[i].name))

    cob.close()


main()

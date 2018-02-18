#
# Project:        cocotb
# File:           file.py
# Date Create:    January 22nd 2018
# Date Modified:  February 18th 2018
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Reads an input file and allows memory-mapped access via python function
# calls. Module does not implement any hardware interfaces to connect it to a
# DUT directly.
#

import mmap

class File(object):
    """ Memory-mapped file.

    Reads an input file and allows memory-mapped access.
    """

    def __init__(self, filename):
        """Initialize.

        Initializes the object. Expects parameter providing the name of the
        file that shall be read.
        """

        # open file and mmap it
        self._file = open(filename, "r+b")
        self._mm = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)

    def close(self):
        """Closes a previously opened file. """

        self._mm.close()
        self._file.close()

    def read(self, addr, size):
        """Reads data from the file (integer in original byte order). """

        return int("".join(self._mm[addr:addr+size]).encode('hex'), 16)

    def read_reverse_byte_order(self, addr, size):
        """Reads data from the file (integer in reversed byte order). """

        # read data and convert to hex string
        data = "".join(self._mm[addr:addr+size]).encode('hex')

        # reverse byte order
        data = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))

        return int(data, 16)

    def size(self):
        """Returns the size of the mmaped file. """

        return len(self._mm)

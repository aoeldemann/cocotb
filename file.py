"""Memory-mapped file access."""
# The MIT License
#
# Copyright (c) 2017-2018 by the author(s)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author(s):
#   - Andreas Oeldemann <andreas.oeldemann@tum.de>
#
# Description:
#
# Reads an input file and allows memory-mapped access via python function
# calls. Module does not implement any hardware interfaces to connect it to a
# DUT directly.

import mmap


class File(object):
    """Memory-mapped file.

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
        """Close file."""
        self._mm.close()
        self._file.close()

    def read(self, addr, size):
        """Read data from the file (integer in original byte order)."""
        return int("".join(self._mm[addr:addr+size]).encode('hex'), 16)

    def read_reverse_byte_order(self, addr, size):
        """Read data from the file (integer in reversed byte order)."""
        # read data and convert to hex string
        data = "".join(self._mm[addr:addr+size]).encode('hex')

        # reverse byte order
        data = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))

        return int(data, 16)

    def size(self):
        """Return the size of the mmaped file."""
        return len(self._mm)

"""CRC checksum calculation."""
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
# CRC checksum calculation.

import struct


def _crc16_initial(c):
    """Create initial CRC16 table values."""
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ 0x1021
        else:
            crc = crc << 1
        c = c << 1
    return crc


# crc16 table
_crc16_tab = [_crc16_initial(i) for i in range(256)]


def _crc16_update(crc, c):
    """CRC16 update function."""
    c = struct.unpack("B", c)[0]
    cc = 0xffff & c
    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _crc16_tab[tmp & 0xff]
    crc = crc & 0xffff
    return crc


def crc16(i):
    """Return the CRC16 value for a given key."""
    h = '%x' % i
    s = ('0'*(len(h) % 2) + h).decode('hex')
    crc = 0
    for c in s:
        crc = _crc16_update(crc, c)
    return crc

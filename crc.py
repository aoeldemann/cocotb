#
# Project:        cocotb
# File:           crc.py
# Date Create:    August 31st 2017
# Date Modified:  August 31st 2017
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Functions to calculate CRC checksums.
#

import struct

def _crc16_initial(c):
    """Creates initial CRC16 table values. """

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
_crc16_tab = [ _crc16_initial(i) for i in range(256) ]

def _crc16_update(crc, c):
    """CRC16 update function. """

    c = struct.unpack("B", c)[0]
    cc = 0xffff & c
    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _crc16_tab[tmp & 0xff]
    crc = crc & 0xffff
    return crc

def crc16(i):
    """Returns the CRC16 value for a given key. """

    h = '%x' % i
    s = ('0'*(len(h) % 2) + h).decode('hex')
    crc = 0
    for c in s:
        crc = _crc16_update(crc, c)
    return crc

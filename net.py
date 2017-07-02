#
# Project:        cocotb
# File:           net.py
# Date Create:    May 17th 2017
# Date Modified:  May 17th 2017
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Provides some handy network related functions.
#

from scapy.all import *
from random import randint
from math import log
from array import array

def gen_packet():
    """Generate a random IP v4/v6, TCP/UDP packet.

    Generates a Scapy IP v4/v6 packet with random source and destination
    addresses, as well as a random length. MAC source and destination addresses
    are fixed.
    """

    # fix source and destination mac adresses
    eth = Ether(dst="53:00:00:00:00:01", src="53:00:00:00:00:02")

    # randomly chose IP v4 or v6 version
    if randint(0, 1) == 0:
        ip = IP(dst=RandIP()._fix(), src=RandIP()._fix())
    else:
        ip = IPv6(src=RandIP6()._fix(), dst=RandIP6()._fix())

    sport = randint(1024, 2**16-1)
    dport = randint(1024, 2**16-1)

    if randint(0, 1) == 0:
        l4 = TCP(sport=sport, dport=dport)
    else:
        l4 = UDP(sport=sport, dport=dport)

    # assemble packet, add random number of random bytes after IP header
    return eth/ip/l4/ \
        ''.join(chr(randint(0, 255)) for _ in range(randint(0, 1000)))

def packet_to_axis_data(pkt, datapath_bit_width):
    """Convert packet to AXI-Stream data.

    Converts a Scapy packet to AXI-Stream data. The function returns a list
    of datapath_bit_width-wide TDATA words and the TKEEP signal that shall be
    placed on the interconnect for the last TDATA word.
    """
    pkt_str = str(pkt)
    tdata = []

    while len(pkt_str) > 0:
        data_len = min(datapath_bit_width/8, len(pkt_str))
        tdata.append(pkt_str[0:data_len])
        pkt_str = pkt_str[data_len:]
        tkeep = 2**data_len-1
    tdata = map(lambda x: int(x[::-1].encode('hex'), 16), tdata)
    return (tdata, tkeep)

def axis_data_to_packet(tdata, tkeep, datapath_bit_width):
    """Convert AXI-Stream data to packet.

    Converts AXI-Stream data to a Scapy packet. The functions expects a list of
    datapath_bit_width-wide TDATA words and the TKEEP signal that was placed
    on the interconnect for the last TDATA word.
    """
    pkt_data = array('B')
    for i, tdata_word in enumerate(tdata):
        if i == len(tdata)-1:
            n_bytes = int(log(tkeep+1, 2))
        else:
            n_bytes = datapath_bit_width/8
        for _ in range(n_bytes):
            pkt_data.append(tdata_word & 0xFF)
            tdata_word >>= 8
    return Ether(pkt_data.tostring())

"""Some handy networking functions."""
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
# Provides some handy network related functions.

from scapy.all import Ether, IP, IPv6, RandIP, RandIP6, TCP, UDP
from math import log
from array import array
from netaddr import IPAddress
from random import randint, random


def gen_packet(eth_only=False):
    """Generate a random network packet.

    By default, function generates a random IPv4 or IPv6 packet, possibly with
    TCP or UDP payloads. If the 'eth_only' parameter is set to True, the
    returned packet is an Ethernet frame that does not include any packet
    headers above layer 2.
    """
    # generate ethernet frame with fixed MAC addresses
    pkt = Ether(src="53:00:00:00:00:01", dst="53:00:00:00:00:02")

    if not eth_only:  # encapsulate IP packet
        if randint(0, 1) == 0:
            pkt /= IP(src=RandIP()._fix(), dst=RandIP()._fix())
        else:
            pkt /= IPv6(src=RandIP6()._fix(), dst=RandIP6()._fix())

        if IP in pkt:  # generated packet L3 is IPv4
            rand = random()
            if rand < 0.1:
                # mark some packets as fragmeents
                if randint(0, 1) == 0:
                    pkt[IP].flags = 1  # set MF flag
                else:
                    pkt[IP].frag = randint(1, 2**13-1)  # frag offset
            elif rand < 0.2:
                # encapsulate an IPv6 packet in some others
                pkt /= IPv6(src=RandIP6()._fix(), dst=RandIP6()._fix())
            elif rand < 0.8:
                # encapsulate TCP / UDP payload in some more
                if randint(0, 1) == 0:
                    pkt /= TCP(sport=randint(0, 2**16-1),
                               dport=randint(0, 2**16-1))
                else:
                    pkt /= UDP(sport=randint(0, 2**16-1),
                               dport=randint(0, 2**16-1))
            else:
                # do not encalsulate in all others
                pass

        elif IPv6 in pkt:  # generated packet L3 is IPv6
            rand = random()
            if rand < 0.8:
                # encapsulate TCP / UDP payload in some more
                if randint(0, 1) == 0:
                    pkt /= TCP(sport=randint(0, 2**16-1),
                               dport=randint(0, 2**16-1))
                else:
                    pkt /= UDP(sport=randint(0, 2**16-1),
                               dport=randint(0, 2**16-1))
            else:
                # encapsulate nothing
                pass

    # append some random payload
    pkt /= ''.join(chr(randint(0, 255)) for _ in
                   range(randint(50, 1000)))

    return pkt


# def gen_packet(gen_ip = True, gen_tcpudp = True):
#    """Generates a random Ethernet frame.
#
#    Generates a Scapy Ethernet Frame that can optionally (by default it does)
#    include an IP v4/v6 packet and a TCP/UDP datagram with random addresses.
#    The generated packet has a random length and random payload contant. MAC
#    source and destination addresses are fixed.
#    """
#
#    # if we want to create a TCP/UDP datagram, for now we can only encapsulate
#    # it in an IP packet
#    if gen_tcpudp:
#        assert gen_ip
#
#    # fix source and destination mac adresses
#    pkt = Ether(dst="53:00:00:00:00:01", src="53:00:00:00:00:02")
#
#    if gen_ip:
#        # randomly chose IP v4 or v6 version
#        if randint(0, 1) == 0:
#            ip = IP(dst=RandIP()._fix(), src=RandIP()._fix())
#        else:
#            ip = IPv6(src=RandIP6()._fix(), dst=RandIP6()._fix())
#
#        pkt = pkt/ip
#
#        if gen_tcpudp:
#            sport = randint(1024, 2**16-1)
#            dport = randint(1024, 2**16-1)
#
#            if randint(0, 1) == 0:
#                l4 = TCP(sport=sport, dport=dport)
#            else:
#                l4 = UDP(sport=sport, dport=dport)
#
#            pkt = pkt/l4
#
#    # add random bytes after IP header
#    return pkt/''.join(chr(randint(0, 255)) for _ in range(randint(50, 1000)))

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


def calc_toeplitz_hash(pkt, key, key_len):
    """Calculate the Toeplitz hash value for an IP packet.

    The function calculates the Toeplitz hash value for an IPv4/IPv6 packet
    than can optionally encapsulate a TCP or UDP L4. The hash value is commonly
    used for receive side scaling. The function expects three inputs: 1) a
    scapy packet, 2) the hash function key and 3) the length of the hash
    function key in bytes.

    For IPv4 packets that are a fragment (i.e. flag MF set or frag. offset
    != 0), the hash value is only calculated based on source and destination
    IP addresses and possible TCP/UDP layers are not taken into account.

    For IPv4 packets that encapsulate an IPv6 packet (i.e. IP6in4, protocol
    number 0x29), the hash is calculated based on the source and destination
    addresses of the inner IPv6 packet. Possible L4 layers within the IPv6
    packet are not taken into account.
    """
    # only calculate toeplitz hash for IPv4 and IPv6 packets
    assert (IP in pkt) or (IPv6 in pkt)

    if IP in pkt:  # L3 is IPv4
        data = int(IPAddress(pkt[IP].src)) << 32
        data |= int(IPAddress(pkt[IP].dst))
        l3 = IP
        dataLen = 64
    elif IPv6 in pkt:  # L3 is IPv6
        data = int(IPAddress(pkt[IPv6].src, 6)) << 128
        data |= int(IPAddress(pkt[IPv6].dst, 6))
        l3 = IPv6
        dataLen = 256

    if l3 == IP and (pkt[IP].flags == 1 or pkt[IP].frag != 0):
        # for fragmented packets, only hash IPv4 header
        pass
    if l3 == IP and IPv6 in pkt[IP]:
        # IPv4 packet encapsulates an IPv6 packet -> calculate hash based on
        # IPv6 source and destination addresses
        data = int(IPAddress(pkt[IPv6].src, 6)) << 128
        data |= int(IPAddress(pkt[IPv6].dst, 6))
        dataLen = 256
    elif TCP in pkt[l3]:  # L4 is TCP
        data = (data << 32) | (pkt[l3][TCP].sport << 16) | pkt[l3][TCP].dport
        dataLen += 32
    elif UDP in pkt[l3]:  # L4 is UDP
        data = (data << 32) | (pkt[l3][UDP].sport << 16) | pkt[l3][UDP].dport
        dataLen += 32

    # initialize data mask
    dataMask = 1 << (dataLen - 1)

    # initialize hash value
    hashval = 0

    # do the hashing
    for i in range(dataLen):
        if data & dataMask:
            hashval ^= (key >> (key_len * 8 - 32 - i)) & 0xFFFFFFFF
        dataMask = dataMask >> 1

    return hashval

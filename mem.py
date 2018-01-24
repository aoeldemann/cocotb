#
# Project:        cocotb
# File:           mem.py
# Date Create:    May 29th 2017
# Date Modified:  January 23rd 2018
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Memory module. Acts as a simplified AXI slave and allows attached DUTs to read
# data from a specific memory location. Writes to the memory are currently only
# possible via python function calls. The AXI slave write interface is not
# implemented.
#

import cocotb
from cocotb.triggers import RisingEdge
from tb import wait_n_cycles, toggle_signal
from random import randint

class Mem(object):
    """ Memory module.

    Acts as a simplified AXI slave that allows attached DUTs to read data from a
    specific memory location. Writes to the memory are currently only possible
    via python function calls. The AXI slave write interface is not implemented.

    """

    def __init__(self, size, offset = 0):
        """Initializes an empty memory with the specified byte size. """

        # initialize empty memory
        self._data = ['\x00'] * size
        self._offset = offset


    def write(self, addr, data, size):
        """Writes data to the memory. """

        assert addr >= self._offset
        addr -= self._offset
        assert (addr + size) <= self.size()

        self._data[addr:addr+size] = data

    def read(self, addr, size):
        """Reads data from the memory (original byte order). """

        assert addr >= self._offset
        addr -= self._offset
        assert (addr + size) <= self.size()

        return int("".join(self._data[addr:addr+size]).encode('hex'), 16)


    def read_reverse_byte_order(self, addr, size):
        """Reads data from the memory (reverse byte order). """

        assert addr >= self._offset
        addr -= self._offset
        assert (addr + size) <= self.size()

        # read data and convert to hex string
        data = "".join(self._data[addr:addr+size]).encode('hex')

        # reverse byte order
        data = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))

        # return data
        return int(data, 16)

    def set_size(self, size):
        """Updates the memory size. """

        self._data = ['\x00'] * size

    def set_offset(self, offset):
        """Updates the memory offset address. """

        self._offset = offset

    def size(self):
        """Returns the memory size. """

        return len(self._data)

    def clear(self):
        """Clears the memory content. """

        for i in range(len(self._data)):
            self._data[i] = '\x00'

    def connect(self, dut, prefix=None):
        """Connects DUT to the AXI slave interface of the memory module. """

        if prefix == None:
            sig_prefix = "m_axi"
        else:
            sig_prefix = "m_axi_%s" % prefix

        self._CLK = dut.clk
        self._ARADDR = getattr(dut, "%s_araddr" % sig_prefix)
        self._ARLEN = getattr(dut, "%s_arlen" % sig_prefix)
        self._ARSIZE = getattr(dut, "%s_arsize" % sig_prefix)
        self._ARVALID = getattr(dut, "%s_arvalid" % sig_prefix)
        self._ARREADY = getattr(dut, "%s_arready" % sig_prefix)
        self._RREADY = getattr(dut, "%s_rready" % sig_prefix)
        self._RDATA = getattr(dut, "%s_rdata" % sig_prefix)
        self._RLAST = getattr(dut, "%s_rlast" % sig_prefix)
        self._RVALID = getattr(dut, "%s_rvalid" % sig_prefix)

    @cocotb.coroutine
    def main(self):
        """AXI slave read interface.

        Allows attached DUT to read memory content via an AXI interface.
        """

        # randomly toggle ARREADY signal
        self._ARREADY <= 1
        cocotb.fork(toggle_signal(self._CLK, self._ARREADY))

        # initially the data invalid
        self._RVALID <= 0

        while True:

            # wait for read request
            while True:
                yield RisingEdge(self._CLK)
                if int(self._ARREADY) and int(self._ARVALID):
                    break

            # save address and burst information
            araddr = int(self._ARADDR)
            arlen = int(self._ARLEN)
            arsize = int(self._ARSIZE)

            # wait random number of clock cycles
            yield wait_n_cycles(self._CLK, randint(1, 40))

            # start answering read request
            for i in range(arlen+1):
                # read data for current burst
                self._RDATA <= \
                        self.read_reverse_byte_order(
                                araddr+i*pow(2, arsize), pow(2, arsize))

                # data is valid
                self._RVALID <= 1

                # set rlast signal high for last beat of the burst
                if i == arlen:
                    self._RLAST <= 1
                else:
                    self._RLAST <= 0

                # wait for requestor to get ready to accept data
                while True:
                    yield RisingEdge(self._CLK)
                    if int(self._RREADY) == 1:
                        break

                # set data to be not valid anymore
                self._RVALID <= 0

                # insert some random gaps between beats of the same burst
                if i != arlen:
                    yield wait_n_cycles(self._CLK, randint(0, 5))

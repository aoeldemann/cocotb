#
# Project:        cocotb
# File:           mem.py
# Date Create:    May 29th 2017
# Date Modified:  February 18th 2018
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Memory module. Acts as a simplified AXI slave and allows attached DUTs to read
# and write data from/to a specific memory location.
#

import cocotb
from cocotb.triggers import RisingEdge
from tb import wait_n_cycles, toggle_signal
import random

class Mem(object):
    """ Memory module.

    Acts as a simplified AXI slave that allows attached DUTs to read and write
    data from/to a specific memory location.
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

        # convert to hex string
        data = "{0:0{1}x}".format(data, 2*size)

        self._data[addr:addr+size] = data.decode('hex')

    def write_reverse_byte_order(self, addr, data, size):
        """Writes data to the memory (reverse byte order). """

        assert addr >= self._offset
        addr -= self._offset
        assert (addr + size) <= self.size()

        # convert to hex string
        data = "{0:0{1}x}".format(data, 2*size)

        # reverse byte order
        data = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))

        self._data[addr:addr+size] = data.decode('hex')

    def read(self, addr, size):
        """Reads data from the memory. """

        assert addr >= self._offset
        addr -= self._offset
        assert (addr + size) <= self.size()

        return int("".join(self._data[addr:addr+size]).encode('hex'), 16)

    def read_reverse_byte_order(self, addr, size):
        """Reads data from the memory (reverse byte order). """

        # read data
        data = self.read(addr, size)

        # convert to hex string
        data = "{0:0{1}x}".format(data, 2*size)

        # reverse byte order
        data = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))

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

        # read interface
        self._ARADDR = getattr(dut, "%s_araddr" % sig_prefix)
        self._ARLEN = getattr(dut, "%s_arlen" % sig_prefix)
        self._ARSIZE = getattr(dut, "%s_arsize" % sig_prefix)
        self._ARVALID = getattr(dut, "%s_arvalid" % sig_prefix)
        self._ARREADY = getattr(dut, "%s_arready" % sig_prefix)
        self._RREADY = getattr(dut, "%s_rready" % sig_prefix)
        self._RDATA = getattr(dut, "%s_rdata" % sig_prefix)
        self._RLAST = getattr(dut, "%s_rlast" % sig_prefix)
        self._RVALID = getattr(dut, "%s_rvalid" % sig_prefix)

        # write interface
        self._AWADDR = getattr(dut, "%s_awaddr" % sig_prefix)
        self._AWLEN = getattr(dut, "%s_awlen" % sig_prefix)
        self._AWSIZE = getattr(dut, "%s_awsize" % sig_prefix)
        self._AWVALID = getattr(dut, "%s_awvalid" % sig_prefix)
        self._AWREADY = getattr(dut, "%s_awready" % sig_prefix)
        self._WREADY = getattr(dut, "%s_wready" % sig_prefix)
        self._WDATA = getattr(dut, "%s_wdata" % sig_prefix)
        self._WLAST = getattr(dut, "%s_wlast" % sig_prefix)
        self._WVALID = getattr(dut, "%s_wvalid" % sig_prefix)
        self._BRESP = getattr(dut, "%s_bresp" % sig_prefix)
        self._BVALID = getattr(dut, "%s_bvalid" % sig_prefix)
        self._BREADY = getattr(dut, "%s_bready" % sig_prefix)

    @cocotb.coroutine
    def main(self):
        """AXI slave read/write interface.

        Allows attached DUT to read/write memory content via an AXI interface.
        """

        # initially read/write address ready signals are low
        self._ARREADY <= 0
        self._AWREADY <= 0

        # initially the read data is invalid
        self._RVALID <= 0

        # initially no write data is accepted
        self._WREADY <= 0

        # initially BVALID is low
        self._BVALID <= 0

        while True: # infinite loop

            read = False
            write = False

            # wait for read/write request
            while True:
                yield RisingEdge(self._CLK)

                # read requests are served before write requests
                if int(self._ARVALID):
                    read = True
                    break

                if int(self._AWVALID):
                    write = True
                    break

            # wait a random number of cycles
            yield wait_n_cycles(self._CLK, random.randint(0, 10))

            if read:
                # acknowledge read request
                self._ARREADY <= 1

                # ARVALID should still be high, but let's explicitly wait and
                # check anyways
                while True:
                    yield RisingEdge(self._CLK)
                    if int(self._ARVALID):
                        break

                # save address and burst information
                araddr = int(self._ARADDR)
                arlen = int(self._ARLEN)
                arsize = int(self._ARSIZE)

                # deassert ARREADY
                self._ARREADY <= 0

                # wait a random number of cycles
                yield wait_n_cycles(self._CLK, random.randint(0, 10))

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
                        yield wait_n_cycles(self._CLK, random.randint(0, 5))

            elif write:
                # acknowledge write request
                self._AWREADY <= 1

                # AWVALID should still be high, but let's explicitly wait and
                # check anyways
                while True:
                    yield RisingEdge(self._CLK)
                    if int(self._AWVALID):
                        break

                # save address and burst information
                awaddr = int(self._AWADDR)
                awlen = int(self._AWLEN)
                awsize = int(self._AWSIZE)

                # deassert AWREADY
                self._AWREADY <= 0

                # wait a random number of cycles
                yield wait_n_cycles(self._CLK, random.randint(0, 10))

                # start write
                for i in range(awlen+1):
                    # accept data
                    self._WREADY <= 1

                    # wait for WVALID to become high
                    while True:
                        yield RisingEdge(self._CLK)
                        if int(self._WVALID):
                            break

                    # get data
                    data = int(self._WDATA)

                    # write data
                    self.write_reverse_byte_order(
                            awaddr+i*pow(2, awsize), data, pow(2, awsize))

                    # check wlast signal
                    if i == awlen:
                        assert int(self._WLAST) == 1
                    else:
                        assert int(self._WLAST) == 0

                    # set WREADY back low
                    self._WREADY <= 0

                    # randomly keep WREADY low sometimes for a bit
                    if i != awlen:
                       if random.random() < 0.1:
                           yield wait_n_cycles(self._CLK, random.randint(1, 5))

                # set BRESP and BVALID
                self._BRESP <= 0
                self._BVALID <= 1

                # wait for BREADY to become high
                while True:
                    yield RisingEdge(self._CLK)
                    if int(self._BREADY):
                        break

                # set BVALID back low
                self._BVALID <= 0


"""Classes for reading/writing AXI4-Lite interfaces."""
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
# Classes for reading/writing AXI4-Lite interfaces.

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import ReturnValue


class AXI_Lite_Writer(object):
    """AXI4-Lite interface writer."""

    def connect(self, dut, clk, bit_width, prefix=None):
        """Connect the DuT AXI4-Lite interface to this writer.

        When parameter 'prefix' is not set, DuT AXI4-Lite signals are expected
        to be named s_axi_awaddr, s_axi_awvalid, ... If 'prefix' is set, DuT
        AXI4-Lite signals are expected to be named s_axi_<prefix>_awaddr, ...
        """
        self.bit_width = bit_width
        self.access_active = False

        if prefix is None:
            sig_prefix = "s_axi"
        else:
            sig_prefix = "s_axi_%s" % prefix

        self.clk = clk
        self.awaddr = getattr(dut, "%s_awaddr" % sig_prefix)
        self.awvalid = getattr(dut, "%s_awvalid" % sig_prefix)
        self.awready = getattr(dut, "%s_awready" % sig_prefix)
        self.wdata = getattr(dut, "%s_wdata" % sig_prefix)
        self.wstrb = getattr(dut, "%s_wstrb" % sig_prefix)
        self.wvalid = getattr(dut, "%s_wvalid" % sig_prefix)
        self.wready = getattr(dut, "%s_wready" % sig_prefix)
        self.bvalid = getattr(dut, "%s_bvalid" % sig_prefix)
        self.bready = getattr(dut, "%s_bready" % sig_prefix)

    @cocotb.coroutine
    def rst(self):
        """Reset signals."""
        self.awvalid <= 0
        self.wvalid <= 0
        self.bready <= 0
        self.wstrb <= 2**(self.bit_width/8)-1
        yield RisingEdge(self.clk)

    @cocotb.coroutine
    def write(self, addr, data):
        """Write data to the AXI4-Lite interface."""
        # serialize access
        while True:
            if not self.access_active:
                break
            yield RisingEdge(self.clk)
        self.access_active = True

        self.awaddr <= addr
        self.awvalid <= 1

        self.wdata <= data
        self.wvalid <= 1

        self.bready <= 1

        while True:
            yield RisingEdge(self.clk)
            if int(self.awready) == 1:
                break

        while True:
            if int(self.wready) == 1:
                break
            yield RisingEdge(self.clk)

        self.awvalid <= 0
        self.wvalid <= 0

        while True:
            yield RisingEdge(self.clk)
            if int(self.bvalid) == 1:
                break

        self.bready <= 0

        yield RisingEdge(self.clk)

        # release access lock
        self.access_active = False


class AXI_Lite_Reader(object):
    """AXI4-Lite interface reader."""

    def connect(self, dut, clk, bit_width, prefix=None):
        """Connect the DuT AXI4-Lite interface to this reader.

        When parameter 'prefix' is not set, DuT AXI4-Lite signals are expected
        to be named s_axi_araddr, s_axi_arvalid, ... If 'prefix' is set, DuT
        AXI4-Lite signals are expected to be named s_axi_<prefix>_araddr, ...
        """
        self.bit_width = bit_width
        self.access_active = False

        if prefix is None:
            sig_prefix = "s_axi"
        else:
            sig_prefix = "s_axi_%s" % prefix

        self.clk = clk
        self.araddr = getattr(dut, "%s_araddr" % sig_prefix)
        self.arvalid = getattr(dut, "%s_arvalid" % sig_prefix)
        self.arready = getattr(dut, "%s_arready" % sig_prefix)
        self.rdata = getattr(dut, "%s_rdata" % sig_prefix)
        self.rvalid = getattr(dut, "%s_rvalid" % sig_prefix)
        self.rready = getattr(dut, "%s_rready" % sig_prefix)

    @cocotb.coroutine
    def rst(self):
        """Reset signals."""
        self.arvalid <= 0
        self.rready <= 0
        yield RisingEdge(self.clk)

    @cocotb.coroutine
    def read(self, addr):
        """Read data from the AXI4-Lite interface."""
        # serialize access
        while True:
            if not self.access_active:
                break
            yield RisingEdge(self.clk)
        self.access_active = True

        self.araddr <= addr
        self.arvalid <= 1

        self.rready <= 1

        while True:
            yield RisingEdge(self.clk)
            if int(self.arready) == 1:
                break

        self.arvalid <= 0

        while True:
            yield RisingEdge(self.clk)
            if int(self.rvalid) == 1:
                break

        self.rready <= 0

        data = int(self.rdata)

        yield RisingEdge(self.clk)

        # release access lock
        self.access_active = False

        raise ReturnValue(data)

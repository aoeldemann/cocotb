"""Classes for reading/writing AXI4-Stream interfaces."""
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
# Classes for reading/writing AXI4-Stream interfaces.

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import ReturnValue
import random


class AXIS_Writer(object):
    """AXI4-Stream interface writer."""

    def connect(self, dut, clk, bit_width, prefix=None):
        """Connect the DuT AXI-Stream interface to this writer.

        When parameter 'prefix' is not set, DUT AXI-Stream signals are expected
        to be named s_axis_tdata, s_axis_tvalid, ... If 'prefix' is set, DuT
        AXI4-Stream signals are expected to be named s_axis_<prefix>_tdata, ...
        """
        self.bit_width = bit_width

        if prefix is None:
            sig_prefix = "s_axis"
        else:
            sig_prefix = "s_axis_%s" % prefix

        self.clk = clk
        self.s_axis_tdata = getattr(dut, "%s_tdata" % sig_prefix)
        self.s_axis_tvalid = getattr(dut, "%s_tvalid" % sig_prefix)
        self.s_axis_tlast = getattr(dut, "%s_tlast" % sig_prefix)
        self.s_axis_tkeep = getattr(dut, "%s_tkeep" % sig_prefix)

        # flow control (tready) is optional
        try:
            self.s_axis_tready = getattr(dut, "%s_tready" % sig_prefix)
            self.has_tready = True
        except AttributeError:
            self.has_tready = False

        # tuser is optional
        try:
            self.s_axis_tuser = getattr(dut, "%s_tuser" % sig_prefix)
            self.has_tuser = True
        except AttributeError:
            self.has_tuser = False

    @cocotb.coroutine
    def rst(self):
        """Reset signals."""
        self.s_axis_tdata <= 0
        self.s_axis_tvalid <= 0
        self.s_axis_tlast <= 0
        self.s_axis_tkeep <= 0
        if self.has_tuser:
            self.s_axis_tuser <= 0
        yield RisingEdge(self.clk)

    @cocotb.coroutine
    def write(self, tdata, tkeep, tuser=None, insert_random_gaps=True):
        """Perform write on AXI4-Stream slave interface.

        Writes a complete transfer on the AXI4-Stream slave interface. The
        function expects a list of the TDATA words and the value of the TKEEP
        signal for the last word transfer. Optionally, a list of TUSER values
        can be specified. If the insert_random_gaps parameter is set to True
        (which is the default), random idle gaps are inserted by setting
        TVALID low.
        """
        for i, word in enumerate(tdata):
            self.s_axis_tdata <= word
            self.s_axis_tvalid <= 1

            if self.has_tuser:
                if i < len(tuser):
                    self.s_axis_tuser <= tuser[i]
                else:
                    self.s_axis_tuser <= 0

            if i == len(tdata)-1:
                self.s_axis_tlast <= 1
                self.s_axis_tkeep <= tkeep
            else:
                self.s_axis_tkeep <= pow(2, self.bit_width/8)-1

            while True:
                yield RisingEdge(self.clk)
                if not self.has_tready or int(self.s_axis_tready) == 1:
                    break

            if insert_random_gaps:
                # with a chance of 20%, insert a clock cycle in which no data
                # is ready to be transmitted by setting tvalid low
                if i != len(tdata)-1 and random.random() < 0.2:
                    self.s_axis_tvalid <= 0
                    yield RisingEdge(self.clk)

        self.s_axis_tvalid <= 0
        self.s_axis_tlast <= 0


class AXIS_Reader(object):
    """AXI4-Stream interface reader."""

    def connect(self, dut, clk, bit_width, prefix=None):
        """Connect the DuT AXI-Stream interface to this reader.

        When parameter 'prefix' is not set, DUT AXI-Stream signals are expected
        to be named m_axis_tdata, m_axis_tvalid, ... If 'prefix' is set, DuT
        AXI4-Stream signals are expected to be named m_axis_<prefix>_tdata, ...
        """
        self.bit_width = bit_width

        if prefix is None:
            sig_prefix = "m_axis"
        else:
            sig_prefix = "m_axis_%s" % prefix

        self.clk = clk
        self.m_axis_tdata = getattr(dut, "%s_tdata" % sig_prefix)
        self.m_axis_tvalid = getattr(dut, "%s_tvalid" % sig_prefix)
        self.m_axis_tlast = getattr(dut, "%s_tlast" % sig_prefix)
        self.m_axis_tkeep = getattr(dut, "%s_tkeep" % sig_prefix)

        # flow control (tready) is optional
        try:
            self.m_axis_tready = getattr(dut, "%s_tready" % sig_prefix)
            self.has_tready = True
        except AttributeError:
            self.has_tready = False

        # tuser is optional
        try:
            self.m_axis_tuser = getattr(dut, "%s_tuser" % sig_prefix)
            self.has_tuser = True
        except AttributeError:
            self.has_tuser = False

    @cocotb.coroutine
    def rst(self):
        """Reset signals."""
        if self.has_tready:
            self.m_axis_tready <= 0
        yield RisingEdge(self.clk)

    @cocotb.coroutine
    def read(self):
        """Perform read on AXI4-Stream master interface.

        Reads a complete transfer on the AXI4-Stream master interface. The
        function returns a list of the TDATA words and the value of the TKEEP
        signal for the last word transfer. If a side-band TUSER interface is
        present, a list of the values is returned as well.
        """
        # empty tdata list
        tdata = []

        if self.has_tuser:
            # empty tuser list
            tuser = []
        else:
            tuser = None

        while True:
            yield RisingEdge(self.clk)

            if (not self.has_tready or int(self.m_axis_tready)) and \
                    int(self.m_axis_tvalid):

                tdata.append(int(self.m_axis_tdata))

                if self.has_tuser:
                    tuser.append(int(self.m_axis_tuser))

                if int(self.m_axis_tlast):
                    tkeep = int(self.m_axis_tkeep)
                    break
                elif int(self.m_axis_tkeep) != pow(2, self.bit_width/8)-1:
                    raise cocotb.result.TestFailure("invalid AXI4-Stream " +
                                                    "TKEEP signal value")

        raise ReturnValue((tdata, tkeep, tuser))

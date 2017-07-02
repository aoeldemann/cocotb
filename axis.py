#
# Project:        cocotb
# File:           axis.py
# Date Create:    May 17th 2017
# Date Modified:  June 30th 2017
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# AXI Stream helper modules that allow easy reading and writing from/to AXI
# master/slave Stream interfaces.
#

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import ReturnValue

class AXIS(object):

    def __init__(self, dut, bit_width, signal_name = None):
        self._clk = dut.clk
        self._bit_width = bit_width

class AXIS_Writer(AXIS):

    def __init__(self, dut, bit_width, signal_name_prefix = None):
        super(self.__class__, self).__init__(dut, bit_width)

        if signal_name_prefix == None:
            self._s_axis_tdata = dut.s_axis_tdata
            self._s_axis_tvalid = dut.s_axis_tvalid
            self._s_axis_tready = dut.s_axis_tready
            self._s_axis_tlast = dut.s_axis_tlast
            self._s_axis_tkeep = dut.s_axis_tkeep
        else:
            self._s_axis_tdata = getattr(dut, "%s_tdata" % signal_name_prefix)
            self._s_axis_tvalid = getattr(dut, "%s_tvalid" % signal_name_prefix)
            self._s_axis_tready = getattr(dut, "%s_tready" % signal_name_prefix)
            self._s_axis_tlast = getattr(dut, "%s_tlast" % signal_name_prefix)
            self._s_axis_tkeep = getattr(dut, "%s_tkeep" % signal_name_prefix)

    def rst(self):
        """Sets AXI Stream master interface signals to reset value. """
        self._s_axis_tdata <= 0
        self._s_axis_tvalid <= 0
        self._s_axis_tlast <= 0
        self._s_axis_tkeep <= 0

    @cocotb.coroutine
    def write(self, tdata, tkeep):
        """Perform write on AXI Stream slave interface.

        Writes a complete transfer on the AXI Stream slave interface. The
        function expects a list of the TDATA words and the value of the TKEEP
        signal for the last word transfer.
        """

        edge = RisingEdge(self._clk)

        for i, word in enumerate(tdata):
            self._s_axis_tdata <= word
            self._s_axis_tvalid <= 1

            if i == len(tdata)-1:
                self._s_axis_tlast <= 1
                self._s_axis_tkeep <= tkeep
            else:
                self._s_axis_tkeep <= pow(2, self._bit_width/8)-1

            while True:
                yield edge
                if int(self._s_axis_tready) == 1:
                    break

        self._s_axis_tvalid <= 0
        self._s_axis_tlast <= 0

class AXIS_Reader(AXIS):

    def __init__(self, dut, bit_width, signal_name_prefix = None):
        super(self.__class__, self).__init__(dut, bit_width)

        if signal_name_prefix == None:
            self._m_axis_tdata = dut.m_axis_tdata
            self._m_axis_tvalid = dut.m_axis_tvalid
            self._m_axis_tready = dut.m_axis_tready
            self._m_axis_tlast = dut.m_axis_tlast
            self._m_axis_tkeep = dut.m_axis_tkeep
        else:
            self._m_axis_tdata = getattr(dut, "%s_tdata" % signal_name_prefix)
            self._m_axis_tvalid = getattr(dut, "%s_tvalid" % signal_name_prefix)
            self._m_axis_tready = getattr(dut, "%s_tready" % signal_name_prefix)
            self._m_axis_tlast = getattr(dut, "%s_tlast" % signal_name_prefix)
            self._m_axis_tkeep = getattr(dut, "%s_tkeep" % signal_name_prefix)

    def rst(self):
        """Sets AXI Stream slave interface signals to reset value. """
        self._m_axis_tready <= 0

    @cocotb.coroutine
    def read(self):
        """Perform read on AXI Stream master interface.

        Reads a complete transfer on the AXI Stream master interface. The
        function returns a list of the TDATA words and the value of the TKEEP
        signal for the last word transfer.
        """
        edge = RisingEdge(self._clk)
        tdata = []

        while True:
            yield edge

            if int(self._m_axis_tready) and int(self._m_axis_tvalid):
                tdata.append(int(self._m_axis_tdata))

                if int(self._m_axis_tlast):
                    tkeep = int(self._m_axis_tkeep)
                    break
                elif int(self._m_axis_tkeep) != pow(2, self._bit_width/8)-1:
                    raise cocotb.result.TestFailure("invalid AXIS tkeep signal")

        raise ReturnValue((tdata, tkeep))

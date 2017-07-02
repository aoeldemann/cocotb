#
# Project:        cocotb
# File:           axilite.py
# Date Create:    May 17th 2017
# Date Modified:  June 7th 2017
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# AXI Lite helper modules that allow easy reading and writing from/to AXI Lite
# peripheral interfaces.
#

import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import ReturnValue

class AXI_Lite(object):

    def __init__(self, data_width):
        self._data_width = data_width

class AXI_Lite_Writer(AXI_Lite):
    """AXI Lite interface writer. """

    def _check_sigs(self):
        """Checks if all required signals are connected. """

        try:
            self._CLK
            self._AWADDR
            self._AWVALID
            self._AWREADY
            self._WDATA
            self._WSTRB
            self._WVALID
            self._WREADY
            self._BVALID
            self._BREADY
        except AttributeError:
            raise Exception("AXI writer signals not set")

    def rst(self):
        """Resets the input signals. """

        self._check_sigs()
        self._AWVALID <= 0
        self._WVALID <= 0
        self._BREADY <= 0
        self._WSTRB <= 2**(self._data_width/8)-1

    @cocotb.coroutine
    def write(self, addr, data):
        """Writes data to the AXI Lite interface. """

        self._check_sigs()
        edge = RisingEdge(self._CLK)

        self._AWADDR <= addr
        self._AWVALID <= 1

        self._WDATA <= data
        self._WVALID <= 1

        self._BREADY <= 1

        while True:
            yield edge
            if self._AWREADY.value == 1:
                break

        while True:
            if self._WREADY.value == 1:
                break
            yield edge

        self._AWVALID <= 0
        self._WVALID <= 0

        while True:
            yield edge
            if self._BVALID.value == 1:
                break

        self._BREADY <= 0

        yield edge

    def connect(self, dut, prefix=None):
        """Connects the DUT AXI Lite interface to this writer.

        When parameter 'prefix' is not set, DUT AXI Lite signals are expected
        to be named s_axi_awaddr, s_axi_awvalid, ... If 'prefix' is set, DUT AXI
        signals are expected to be named s_axi_<prefix>_awaddr, ...
        """

        if prefix == None:
            sig_prefix = "s_axi"
        else:
            sig_prefix = "s_axi_%s" % prefix

        self._CLK = dut.clk
        self._AWADDR = getattr(dut, "%s_awaddr" % sig_prefix)
        self._AWVALID = getattr(dut, "%s_awvalid" % sig_prefix)
        self._AWREADY = getattr(dut, "%s_awready" % sig_prefix)
        self._WDATA = getattr(dut, "%s_wdata" % sig_prefix)
        self._WSTRB = getattr(dut, "%s_wstrb" % sig_prefix)
        self._WVALID = getattr(dut, "%s_wvalid" % sig_prefix)
        self._WREADY = getattr(dut, "%s_wready" % sig_prefix)
        self._BVALID = getattr(dut, "%s_bvalid" % sig_prefix)
        self._BREADY = getattr(dut, "%s_bready" % sig_prefix)

class AXI_Lite_Reader(AXI_Lite):
    """AXI Lite interface reader. """

    def _check_sigs(self):
        """Checks if all required signals are connected. """

        try:
            self._CLK
            self._ARADDR
            self._ARVALID
            self._ARREADY
            self._RDATA
            self._RVALID
            self._RREADY
        except AttributeError:
            raise Exception("AXI reader signals not set")

    def rst(self):
        """Resets the input signals. """

        self._check_sigs()
        self._ARVALID <= 0
        self._RREADY <= 0

    @cocotb.coroutine
    def read(self, addr):
        """Reads data from the AXI Lite interface. """

        self._check_sigs()
        edge = RisingEdge(self._CLK)

        self._ARADDR <= addr
        self._ARVALID <= 1

        self._RREADY <= 1

        while True:
            yield edge
            if self._ARREADY.value == 1:
                break

        self._ARVALID <= 0

        while True:
            yield edge
            if self._RVALID.value == 1:
                break

        self._RREADY <= 0

        data = int(self._RDATA.value)

        yield edge

        raise ReturnValue(data)

    def connect(self, dut, ident=None):
        """Connects the DUT AXI Lite interface to this reader.

        When parameter 'prefix' is not set, DUT AXI Lite signals are expected
        to be named s_axi_araddr, s_axi_arvalid, ... If 'prefix' is set, DUT AXI
        signals are expected to be named s_axi_<prefix>_araddr, ...
        """

        if ident == None:
            sig_prefix = "s_axi"
        else:
            sig_prefix = "s_axi_%s" % ident

        self._CLK = dut.clk
        self._ARADDR = getattr(dut, "%s_araddr" % sig_prefix)
        self._ARVALID = getattr(dut, "%s_arvalid" % sig_prefix)
        self._ARREADY = getattr(dut, "%s_arready" % sig_prefix)
        self._RDATA = getattr(dut, "%s_rdata" % sig_prefix)
        self._RVALID = getattr(dut, "%s_rvalid" % sig_prefix)
        self._RREADY = getattr(dut, "%s_rready" % sig_prefix)

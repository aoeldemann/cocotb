#
# Project:        cocotb
# File:           tb.py
# Date Create:    May 17th 2017
# Date Modified:  August 25th 2017
# Author:         Andreas Oeldemann, TUM <andreas.oeldemann@tum.de>
#
# Description:
#
# Provides some basic test bench functions that are needed quite frequently.
#


import cocotb
from cocotb.triggers import Timer, RisingEdge
from random import randint

@cocotb.coroutine
def clk_gen(sig_clk, freq_mhz):
    """ Generates a clock with a specifiable clock frequency in MHz. """
    t_clk = 1e6/freq_mhz
    while True:
        sig_clk <= 0
        yield Timer(t_clk/2)
        sig_clk <= 1
        yield Timer(t_clk/2)

@cocotb.coroutine
def wait_n_cycles(sig_clk, n_cycles):
    """ Waits a specific number of rising clock events. """
    for _ in range(n_cycles):
        yield RisingEdge(sig_clk)

@cocotb.coroutine
def rst(sig_clk, sig_rst):
    """ Resets the DUT.

    Triggers the reset signal of the DUT for 5 clock cycles. Provided reset
    signal must be active high.
    """
    yield RisingEdge(sig_clk)
    sig_rst <= 1
    yield wait_n_cycles(sig_clk, 5)
    sig_rst <= 0
    yield RisingEdge(sig_clk)

@cocotb.coroutine
def rstn(sig_clk, sig_rstn):
    """ Resets the DUT.

    Triggers the reset signal of the DUT for 5 clock cycles. Provided reset
    signal must be active low.
    """
    yield RisingEdge(sig_clk)
    sig_rstn <= 0
    yield wait_n_cycles(sig_clk, 5)
    sig_rstn <= 1
    yield RisingEdge(sig_clk)

@cocotb.coroutine
def toggle_signal(clk, sig):
    """Randomly toggles the value of a one bit signal. """
    while True:
        yield wait_n_cycles(clk, randint(1, 25))
        if int(sig) == 0:
            sig <= 1
        else:
            sig <= 0

def check_value(name, val1, val2):
    """Checkes whether two values are equal. Throws error if not. """

    if val1 == val2:
        return

    msg = "Incorrect value '%s': 0x%x != 0x%x" % (name, val1, val2)
    raise cocotb.result.TestFailure(msg)

def swp_byte_order(data, bytelen):
    """Returns the input data in reversed byte oder """

    h = '%x' % data
    s = ('0'*(len(h) % 2) + h).zfill(bytelen*2).decode('hex')
    return int(s[::-1].encode('hex'), 16)

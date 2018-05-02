"""Basic test bench functions."""
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
# Provides some basic test bench functions that are needed quite frequently.

import cocotb
from cocotb.triggers import Timer, RisingEdge
from random import randint
import numpy as np
import sys


@cocotb.coroutine
def clk_gen(sig_clk, freq_mhz):
    """Generate a clock with a specifiable clock frequency in MHz."""
    t_clk = 1e6/freq_mhz
    while True:
        sig_clk <= 0
        yield Timer(t_clk/2)
        sig_clk <= 1
        yield Timer(t_clk/2)


@cocotb.coroutine
def wait_n_cycles(sig_clk, n_cycles):
    """Wait a specific number of rising clock events."""
    for _ in range(n_cycles):
        yield RisingEdge(sig_clk)


@cocotb.coroutine
def rst(sig_clk, sig_rst):
    """Reset the DuT.

    Trigger the reset signal of the DuT for 5 clock cycles. Provided reset
    signal must be active high.
    """
    yield RisingEdge(sig_clk)
    sig_rst <= 1
    yield wait_n_cycles(sig_clk, 5)
    sig_rst <= 0
    yield RisingEdge(sig_clk)


@cocotb.coroutine
def rstn(sig_clk, sig_rstn):
    """Reset the DuT.

    Trigger the reset signal of the DuT for 5 clock cycles. Provided reset
    signal must be active low.
    """
    yield RisingEdge(sig_clk)
    sig_rstn <= 0
    yield wait_n_cycles(sig_clk, 5)
    sig_rstn <= 1
    yield RisingEdge(sig_clk)


@cocotb.coroutine
def toggle_signal(clk, sig):
    """Randomly toggle the value of a one bit signal."""
    while True:
        yield wait_n_cycles(clk, randint(1, 25))
        if int(sig) == 0:
            sig <= 1
        else:
            sig <= 0


def check_value(name, val1, val2):
    """Check whether two values are equal. Throw error if not."""
    if val1 == val2:
        return

    msg = "Incorrect value '%s': 0x%x != 0x%x" % (name, val1, val2)
    raise cocotb.result.TestFailure(msg)


def swp_byte_order(data, bytelen):
    """Return the input data in reversed byte order."""
    h = '%x' % data
    s = ('0'*(len(h) % 2) + h).zfill(bytelen*2).decode('hex')
    return int(s[::-1].encode('hex'), 16)


def print_progress(i, n):
    """Print simulation progress.

    Parameter 'i' defines the current iteration number (0 <= i < n). Parameter
    'n' defines the total number of iterations.
    """
    # calculate iteration thresholds on which print out shall occur
    thresholds = np.arange(n/10-1, n, n/10)

    if i == 0:
        # this is the first iteration
        print("Status: 0% ..."),
        sys.stdout.flush()
    if i in thresholds:
        # print out progress
        print("%d%% ..." % int(100.0*float(i+1)/float(n))),
        sys.stdout.flush()
    if i == n-1:
        # this is the last iteration
        print("done!")

# cocotb library

This repository contains some helpful
[cocotb](http://potential.ventures/cocotb/) classes and functions that I
frequently use to write test benches for RTL hardware code.

## axilite.py

AXI Lite helper modules that allow easy reading and writing from/to AXI Lite
peripheral interfaces.

## axis.py

AXI Stream helper modules that allow easy reading and writing from/to AXI
master/slave Stream interfaces.

## crc.py

Functions to calculate CRC checksums.

## file.py

Reads an input file and allows memory-mapped access via python function
calls. Module does not implement any hardware interfaces to connect it to a
DUT directly.


## mem.py

Memory module. Acts as a simplified AXI slave and allows attached DUTs to read
and write data from/to a specific memory location.

## net.py

Provides some handy network related functions.

## tb.py

Provides some basic test bench functions that are needed quite frequently.

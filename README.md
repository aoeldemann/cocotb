# cocotb library

This repository contains some helpful cocotb classes and functions that I
frequently use to write test benches for RTL hardware code.

## axilite.py

Contains `AXI_Lite_Writer` and `AXI_Lite_Reader` classes. They allow for easy
writing and reading to/from a device-under-test via an AXI4-Lite interface.

## axis.py

Contains `AXIS_Writer` and `AXIS_Reader` classes. They allow for easy writing
and reading to/from a device-under-test via an AXI4-Stream interface.

## mem.py

Contains a simple model of a random-access memory, which can be read from via
an AXI4 interface. The memory returns read data from a file provided as an
input. Writes are not yet implemented. The AXI4 interface is simplified (e.g.
only incremental bursts, no QoS, no locking, ...).

## net.py

Contains network related helper functions (e.g. generate random packet,
convert packet to/from AXI4-Stream format, ...). Makes use of the Python Scapy
library.

## tb.py

Contains essential helper for clock generation, device-under-test reset,
random signal toggeling, ...

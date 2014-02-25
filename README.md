# Lattice iCEBlink40 Programming Tool

The Lattice iCEBlink40 is a low-cost FPGA board (currently $50 cad) supporting the iCE40 LP/HX families. While the iCEcube programming software on linux supports the chips, it doesn't ship with a port of iceutil.exe to program the board itself. This is an open-source tool, licensed under GPL2, to allow for programming of the FPGA board from linux. 

This script has only been tested with the iCEblink40-LP1K board, with the M25P10VP flash.

This tool was created from black-box inspection of the USB datastream between a VM running iceutil and the iCEblink40-LP1K evaluation board. No binary analysis, binary reverse engineering or disassembly was used during the creation of this tool; all information in this file was derived from black-box analysis.

# Requirements:

- python 3 or newer
- pyusb 1.0 or newer

# Usage - iCEburn.py

./iCEburn.py -v -e -w path\_to\_build.bin

# regtool

Regtool is an example test script to poke at registers via the FPGA data link. The argument

    -r 0xAB

will do a read of register 0xAB and print the result to the console. The argument

    -w 0xAB:0xCD
 
will write register 0xAB with value and print the result to the console. With the stock FPGA firmware
 
    ./regtool.py -w 5:0x48

will stop the scrolling pattern and fix LED3 on.

Regtool is primarily intended as an example of API usage, and not as a production grade tool.


# Bugs

- If using old versions of pyUSB, you may get an error:

    AttributeError: "'NoneType' object has no attribute 'libusb_exit'"

This is a bug in pyusb.


# TODO

- Verify on HX1K board

- Add additional flash devices


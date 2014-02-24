# Lattice iCEBlink40 Programming Tool

The Lattice iCEBlink40 is a low-cost FPGA board (currently $50 cad) supporting the iCE40 LP/HX families. While the iCEcube programming software on linux supports the chips, it doesn't ship with a port of iceutil.exe to program the board itself. This is an open-source tool, licensed under GPL2, to allow for programming of the FPGA board from linux. 

This script has only been tested with the iCEblink40-LP1K board, with the M25P10VP flash.

This tool was created from black-box inspection of the USB datastream between a VM running iceutil and the iCEblink40-LP1K evaluation board. No binary analysis, binary reverse engineering or disassembly was used during the creation of this tool; all information in this file was derived from black-box analysis.

# Requirements:

- python 3 or newer
- pyusb 1.0 or newer

# Usage

./iCEburn.py -v -e -w path\_to\_build.bin

# Bugs

- If using old versions of pyUSB, you may get an error:

    AttributeError: "'NoneType' object has no attribute 'libusb_exit'"

This is a bug in pyusb.


# TODO

- The microcontroller on the PCB seems to support FPGA<->host communications passthrough. This functionality should be implemented.

- Verify on HX1K board

- Add additional flash devices


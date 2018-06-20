#!/usr/bin/python3

import argparse
from iCEburn.libiceblink import ICE40Board

def rtype(x):
    return ('R', int(x, 16))

def wtype(x):
    return ('W', [int(i,16) for i in x.split(':')])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--read", dest='actions', type=rtype, action='append')
    ap.add_argument("-w", "--write", dest='actions', type=wtype, action='append')
    args = ap.parse_args()

    board = ICE40Board()
    with board.get_board_comm() as comm:
        for atype, arg in args.actions:
            if atype == 'R':
                addr = arg
                print("READ  %02x: %02x" % (addr, comm.readReg(addr)))
            elif atype == 'W':
                addr, value = arg
                print("WRITE %02x: %02x" % (addr, value))
                comm.writeReg(addr, value)


if __name__ == "__main__":
    main()

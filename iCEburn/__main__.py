#!/usr/bin/python3
import argparse
from iCEburn.libiceblink import ICE40Board, M25P10

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--erase", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-w", "--write", type=argparse.FileType("rb"))
    args = ap.parse_args()

    board = ICE40Board()

    if args.verbose:
        print("Found iCE40 board serial: %s" % board.get_serial())


    sp = board.get_spi_port(0)

    with board.get_gpio() as gpio:
        # Force the FPGA into reset so we may drive the IOs
        gpio.ice40SetReset(True)

        with board.get_spi_port(0) as sp:
            sp.setSpeed(50000000)
            sp.setMode()

            flash = M25P10(sp.io)

            flash.wakeup()
            
            # Verify that we're talking to the part we think we are
            assert flash.getID() == b'\x20\x20\x11'

            # Now, do the actions
            if args.erase:
                if args.verbose:
                    print("Erasing flash...")
                flash.chipErase()
                if args.verbose:
                    print("")

            if args.write:
                data = args.write.read()

                if args.verbose:
                    print("Writing image...")

                for addr in range(0, len(data), 256):
                    buf = data[addr:addr+256]
                    flash.pageProgram(addr, buf)

                if args.verbose:
                    print("Verifying written image...")
                # Now verify
                buf = flash.read(0, len(data))
                assert len(buf) == len(data)
            
                nvfailures = 0
                for i,(a,b) in enumerate(zip(buf, data)):
                    if a!=b:
                        print ("verification failure at %06x: %02x != %02x" %
                               (i,a,b))
                        nvfailures += 1

                    if nvfailures == 5:
                        print("Too many verification failures, bailing")
                        break

        # Release the FPGA reset
        gpio.ice40SetReset(False)


if __name__ == "__main__":
    main()

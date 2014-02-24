#!/usr/bin/python3.3

import usb.core
import usb.util
import array
import struct
import binascii
import time

class ProtocolError(Exception):
    pass

class SPIProtocolError(Exception):
    def __init__(self, cmd, rescode):
        lut = {
            3: "Resource in use",
            12: "Invalid enum"
        }
        if rescode in lut:
            err = lut[rescode]
        else:
            err = "error code %d" % rescode

        ProtocolError.__init__(self, "Command %s failed with error: %s" %( cmd,
                               err))

class ICE40Board(object):

    CMD_GET_BOARD_TYPE = 0xE2
    CMD_GET_BOARD_SERIAL = 0xE4

    class __ICE40SPIPort(object):
        def __init__(self, dev, portno):
            self.__portno = portno
            self.__is_open = False

        def __enter__(self):
            self.open()

        def __exit__(self, type, exc, traceback):
            self.__cleanup()

        def __del__(self):
            self.__cleanup()

        def __cleanup(self):
            if self.__is_open:
                self.close()

        def open(self):
            pass

        def close(self):
            pass

    def get_spi_port(self, pn):
        return self.__ICE40SPIPort(self.dev, pn)

    def __init__(self):
        # find our self.device
        self.dev = usb.core.find(idVendor=0x1443, idProduct=0x0007)

        # was it found?
        if self.dev is None:
            raise ValueError('Device not found')

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()
        
        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = usb.util.find_descriptor(cfg)

        self.ep_cmdout  = usb.util.find_descriptor(intf, bEndpointAddress = 1)
        self.ep_cmdin   = usb.util.find_descriptor(intf, bEndpointAddress = 0x82)
        self.ep_dataout = usb.util.find_descriptor(intf, bEndpointAddress = 3)
        self.ep_datain  = usb.util.find_descriptor(intf, bEndpointAddress = 0x84)

        assert self.ep_cmdout is not None
        assert self.ep_cmdin is not None
        assert self.ep_dataout is not None
        assert self.ep_datain is not None

        # Make sure we're talking to what we expect
        btype = self.get_board_type()
        assert btype == 'iCE40'

        #print("ser:  %s" % self.get_board_serial())

        # Unknown - returns 2E0140F0
        #self.ctrl(0xE9, 0x04)

        # Unknown - returns 16000000
        #self.ctrl(0xE7, 8)

        #self.ctrl(0xE9, 0x04)

        # Handshake - 0xE8 sends a 2-byte value, 0xEC returns 'igiD' ^ value
        #self.ctrl(0xE8, [0x9d, 0x01])
        #buf = self.ctrl(0xEC, 0x04) 
        #assert buf == b'igiD'
        #self.ctrl(0xE8, [0x00,0x00])


        # Seems to return 0x7A - value
        #self.cmd(0x0, 0x03, [0x00, 0x01, 0x00, 0x00, 0x00], 16,
        #                show=True)

        return

        spi_is_open = 0
        gpio_is_open = 0
        try:
            self.spi_open(0)
            spi_is_open = True
            self.spi_unk()
            self.spi_speed(50000000)


            print (self.checked_cmd(0x03, 0x02, "0302", [0x00, 0x01]))
            print (self.checked_cmd(0x03, 0x02, "0302", [0x00, 0x05]))

            # Some kind of open
            self.checked_cmd(0x03, 0x00, "gpioopen", [0x00], noret=True)
            gpio_is_open=True
            
            ## Put FPGA to sleep 
            # Dir?
            self.checked_cmd(0x03, 0x04, "0304", [0x00, 0x01, 0x00, 0x00,
                                                        0x00],show=True)
            # Value?
            self.checked_cmd(0x03, 0x06, "0306", [0x00, 0x00, 0x00, 0x00,
                                                         0x00],
                             noret=True)

            # Wakeup the SPI part
            self.spi_io([0xab, 0x00, 0x00, 0x00])

            # Validate that the flash is the M25P10
            assert self.spi_get_id() == b'\x20\x20\x11'

            self.spi_chip_erase()

            # Value?
            self.checked_cmd(0x03, 0x06, "0306", [0x00, 0x01, 0x00, 0x00,
                                                         0x00],
                             noret=True)

        finally:
            if gpio_is_open:
                self.checked_cmd(0x03, 0x01, "gpioclose", 0x00)
            if spi_is_open:
                self.checked_cmd(0x06, 0x06, "0606", [0x00, 0x01])
                self.spi_close(0)

    def spi_set_writable(self):
        self.spi_io([0x06])
        print("%02x" % self.spi_get_status())

    def spi_chip_erase(self):
        self.spi_set_writable()
        self.spi_io([0xC7])
        self.spi_wait_done()

    def spi_wait_done(self):
        while self.spi_get_status() & 0x1:
            pass

    def spi_get_status(self):
        return self.spi_io([0x05],2)[1]

    def spi_get_id(self):
        return self.spi_io([0x9F],4)[1:]

    def spi_io(self, write_bytes, read_byte_count=0):
        write_bytes = list(write_bytes)

        # Pad write count
        if len(write_bytes) < read_byte_count:
            write_bytes.extend([0] * (read_byte_count - len(write_bytes)))

        write_byte_count = len(write_bytes)

        read_bytes = []

        # Set CS?
        self.checked_cmd(0x06, 0x06, "0606", [0x00, 0x00])


        # Start IO txn
        self.checked_cmd(0x06, 0x07, "0607", 
                         struct.pack("<BBBBL", 0x00, 0x00, 0x00, 
                                     0x01 if read_byte_count else 0x00,
                                     write_byte_count),noret=True)

        # Do the IO
        while write_bytes or len(read_bytes) < read_byte_count:
            if write_bytes:
                self.ep_dataout.write(write_bytes[:64])
                write_bytes = write_bytes[256:]

            if read_byte_count:
                to_read = min(64, read_byte_count) 
                read_bytes.extend(self.ep_datain.read(to_read))



        # End IO txn
        status, resb =self.cmd(0x06, 0x87,[0x00])
       
        # status & 0x80 indicates presence of write size
        # status & 0x40 indicates presence of read size

        if status & 0x80:
            wb = struct.unpack('<L', resb[:4])[0]
            resb = resb[4:]
            assert wb == write_byte_count
            
        if status & 0x40:
            rb = struct.unpack('<L', resb[:4])[0]
            resb = resb[4:]
            assert rb == read_byte_count

        # Clear CS
        self.checked_cmd(0x06, 0x06, "0606", [0x00, 0x01])

        return bytes(read_bytes)

    def spi_open(self, portno):
        pl = self.checked_cmd(0x06, 0x00, "SPIOpen", [portno])
        assert len(pl) == 0

    def spi_close(self, portno):
        pl = self.checked_cmd(0x06, 0x01, "SPIClose", [portno])
        assert len(pl) == 0

    def spi_unk(self):
        """May be mode-setting. [0,2] causes bits to be returned shifted right
        one"""
        # 202011
        # 901008
        pl = self.checked_cmd(0x06, 0x05, "SpiMode", [0,0])
        assert len(pl) == 0

    def spi_speed(self, speed):
        """ sets the desired speed for the SPI interface. Returns actual speed
        set"""
        pl = self.checked_cmd(0x06, 0x03, "SPISpeed", b'\x00' + struct.pack("<L",
                                                                  speed),show=False)

        return (struct.unpack("<L",pl),)


    def ctrl(self, selector, size_or_data, show=False):
        val = self.dev.ctrl_transfer(0xC0 if isinstance(size_or_data, int) else 0x04, 
                          selector, 0x00, 0x00, size_or_data)
        if show and isinstance(val, array.array):
            print("%2x < %s" % (selector, "".join("%02x" % i for i in val)))
        return bytes(val)

    def checked_cmd(self, cmd, subcmd, name, payload=[], ressize=16, show=False,
                   noret=False):
        status, respl = self.cmd(cmd, subcmd, payload, ressize, show)
        if status != 0:
            raise SPIProtocolError(name, status)
        if noret:
            assert len(respl) == 0
        return respl

    def cmd(self, cmd, subcmd, payload, ressize=16, show=False):
        res = self.cmd_i(
            struct.pack("<BB", cmd, subcmd) + bytes(payload),
            ressize)

        status = res[0]
        if show:
            print ("%02x:%02x (%s) < %02x:(%s)" % (cmd, subcmd,
                                              binascii.hexlify(bytes(payload)).decode('ascii'),
                                              status,
                                                   binascii.hexlify(res[1:]).decode('ascii')))
        return status, res[1:]

    def cmd_i(self, cmd_bytes, result_size, show=False):
        payload = struct.pack('<B', len(cmd_bytes)) + bytes(cmd_bytes)
        self.ep_cmdout.write(payload)
        res = bytes(self.ep_cmdin.read(result_size))

        if show:
            print("%s:%s" % (binascii.hexlify(payload).decode('ascii'),
                             binascii.hexlify(res).decode('ascii')))
        assert res[0] == len(res[1:])
        return res[1:]

    def get_board_type(self):
        btype = self.ctrl(0xE2, 16)
        return btype[:btype.index(b'\x00')].decode('ascii')

    def get_board_serial(self):
        return self.ctrl(0xE4, 16).decode('ascii')

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--erase", action="store_true")
    args = ap.parse_args()

    board = ICE40Board()


    sp = board.get_spi_port(0)

    with sp:
        pass

if __name__ == "__main__":
    main()

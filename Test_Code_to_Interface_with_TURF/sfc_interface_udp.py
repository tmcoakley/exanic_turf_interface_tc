# class for turf packet interface, bytes object is created at initialization, 4 bytes long only or else 4 bytes of all 0.
# to get just a byte from a bytes object, .,...
# eventually, need a packet class that expands on this, initializing with zero-filled bytes object of max length: bytes(MAX_LENGTH)
import socket


# USER INPUT
ATTEMPT = 2  #  this is the number of times to attempt a connection
TIMEOUT = 1  #  the time to wait for a response, written in seconds

# TURF IP AND PORTS
UDP_IP = "127.0.0.3"
UDP_RD = 21618  # read port in decimal
UDP_WR = 21623  # write port in decimal

# Constants for receiving
TAG_REC = b"\x00\x00\x00\x00\xF0\x00\x00\x00"
TAG_REC_bytearray = 0b11110000  # this is a bytes class ARRAY
ADDR_REC = b"\x00\x00\x00\x00\x0F\xFF\xFF\xFF"
ADDR_REC_bytearray = 0x0FFFFFFF  # this is a bytes ARRAY
DATA_REC = b"\xFF\xFF\xFF\xFF\x00\x00\x00\x00"
DATA_REC_bytearray = 0xFFFFFFFF

# listen for return packets on the b'Tx' port.
UDP_TX = b"Tx"  # in hex would be: 0x5478, instead decimal: 21,624
ENDI = "little"


class Packet:
    def __init__(self, host, port):
        self.cs = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  # create a control socket
        self.cs.bind((host, port))  # have to bind to port to make it bidirectional

    def read(self, hdr):
        self.sending_port = UDP_RD  # 'Tr' --> receives read requests
        self.data = hdr[::-1]
        self.recd()
        return self.ack

    def write(self, hdr, value):
        self.sending_port = UDP_WR  # 'Tw' --> receives write requests
        hdr = hdr[::-1]
        value = value[::-1]
        self.data = value + hdr
        self.recd()
        return self.ack

    def recd(self):
        self.attempt = ATTEMPT
        self.cs.settimeout(
            TIMEOUT
        )  # sets the parameter for how long you want to listen for a response on the client side
        self.cs.connect((UDP_IP, self.sending_port))  # connect to the correct port
        while True:
            if self.attempt == 0:  # if you finish an alloted amount of attempts
                break
            else:
                self.conn()
                if self.is_recv is True:
                    break
                self.attempt -= 1

    def conn(self):
        self.is_recv = False  # indicates whether a response has been received
        self.cs.sendto(self.data, (UDP_IP, self.sending_port))
        try:  # attempts to receive a response
            # if a response is received, save value
            message, _ = self.cs.recvfrom(1024)  # can format to save returning address
            self.ack = message[::-1]
            self.recd_parser(self.ack)
            self.is_recv = True
        except Exception:
            self.ack = (
                ""  # if no response is received, indicate there wasn't a response
            )

    def print_ack(self):  # prints what is sent back from the server
        if self.is_recv is True:
            print("Received: {}".format(self.ack.hex("x")))
            print("Data with Incremented Tag: {}".format(self.rec_inc.hex("x")))
            print(
                "Acknowledged after {} attempt(s)".format((ATTEMPT + 1) - self.attempt)
            )

        else:
            print("No acknowledgement after {} attempts".format(ATTEMPT))

    def recd_parser(
        self, totalData
    ):  # parser for received data from the TURF, will be 64 bits regardless of read/write

        self.recdata = self.general_parser(totalData, DATA_REC)

        self.datarecd = (
            (self.recdata[0] << 24)
            | (self.recdata[1] << 16)
            | (self.recdata[2] << 8)
            | self.recdata[3]
        ) & DATA_REC_bytearray

        self.rectag = self.general_parser(totalData, TAG_REC)
        self.tagrecd = self.rectag[4] & TAG_REC_bytearray
        self.tagincr = self.tagrecd + 16

        self.recaddr = self.general_parser(totalData, ADDR_REC)

        self.addrrecd = (
            (self.recaddr[4]) << 24
            | (self.recaddr[5] << 16)
            | (self.recaddr[6] << 8)
            | self.recaddr[7]
        ) & ADDR_REC_bytearray

        self.rec_inc = (
            self.datarecd.to_bytes(4, "big")
            + self.tagincr.to_bytes(1, "big")
            + self.addrrecd.to_bytes(3, "big")
        )

    def general_parser(self, bytestr, bytecomp):
        return (
            int.from_bytes(bytestr, ENDI) & int.from_bytes(bytecomp, ENDI)
        ).to_bytes((len(bytestr)), ENDI)

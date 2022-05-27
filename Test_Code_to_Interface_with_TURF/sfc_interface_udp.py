# class for turf packet interface, bytes object is created at initialization, 4 bytes long only or else 4 bytes of all 0.
# to get just a byte from a bytes object, .,...
# eventually, need a packet class that expands on this, initializing with zero-filled bytes object of max length: bytes(MAX_LENGTH)
import socket

# Constants for sending
ADDR_C = b"\x0F\xFF\xFF\xFF"  # this is a bytes class
ADDR_bytearray = 0x0FFFFFFF  # this is a bytes ARRAY
TAG_C = b"\xF0\x00\x00\x00"  # this is a bytes class
TAG_bytearray = 0b11110000  # this is a bytes class ARRAY

# Constants for receiving
TAG_REC = b"\x00\x00\x00\x00\xF0\x00\x00\x00"
ADDR_REC = b"\x00\x00\x00\x00\x0F\xFF\xFF\xFF"
DATA_REC = b"\xFF\xFF\xFF\xFF\x00\x00\x00\x00"
DATA_REC_bytearray = 0xFFFFFFFF

# 2 byte ascii are b'Tr' and b'Tw' respectively, these are ports (note difference to addresses in a packet which is sent to a port)
UDP_RD = b"\x54\x72"  # this is in hex, instead decimal: 21618 # obviously for reads
UDP_WR = b"\x54\x77"  # this is in hex, instead decimal: 21623 # obviously for writes

# listen for return packets on the b'Tx' port.
UDP_TX = b"Tx"  # in hex would be: 0x5478, instead decimal: 21,624
ENDI = "little"
UDP_IP = "192.168.1.128"

ATTEMPT = 2  #  this is the number of times to attempt a connection
TIMEOUT = 1  #  the time to wait for a response, written in seconds

MY_IP = "192.168.1.1"
MY_PORT = 21347


class packet:
    def __init__(self):
        self.cs = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  # create a control socket
        self.cs.bind((MY_IP, MY_PORT))  # have to bind to port to make it bidirectional

    def read(self, hdr):
        self.sending_port = 21618  # 'Tr' --> receives read requests
        self.hdr = hdr[::-1]
        self.recd()

    def write(self, hdr):
        self.sending_port = 21623  # 'Tw' --> receives write requests
        self.hdr = hdr[::-1]
        self.recd()

    def recd(self):
        self.attempt = ATTEMPT
        self.cs.settimeout(
            TIMEOUT
        )  # sets the parameter for how long you want to listen for a response on the client side
        self.cs.connect(
            (UDP_IP, self.sending_port)
        )  # connect to the correct port
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
        self.cs.sendto(self.hdr, (UDP_IP, self.sending_port))
        try:  # attempts to receive a response
            # if a response is received, save value
            message, _ = self.cs.recvfrom(
                1024
            )  # can format to save returning address
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
            print(
                "Acknowledged after {} attempt(s)".format((ATTEMPT + 1) - self.attempt)
            )

        else:
            print("No acknowledgement after {} attempts".format(ATTEMPT))

    def recd_parser(
        self, totalData
    ):  # parser for received data from the TURF, will be 64 bits regardless of read/write
        
        self.general_parser(totalData, DATA_REC)
        self.recdata = self.parseddata

        self.datarecd = (
            (self.recdata[0] << 24)
            | (self.recdata[1] << 16)
            | (self.recdata[2] << 8)
            | self.recdata[3]
        ) & DATA_REC_bytearray

        self.general_parser(totalData, TAG_REC)
        self.rectag = self.parseddata

        self.tagrecd = self.rectag[4] & TAG_bytearray

        self.general_parser(totalData, ADDR_REC)
        self.recaddr = self.parseddata

        self.addrrecd = (
            (self.recaddr[4]) << 24
            | (self.recaddr[5] << 16)
            | (self.recaddr[6] << 8)
            | self.recaddr[7]
        ) & ADDR_bytearray

    def general_parser(self, bytestr, bytecomp):
        self.parseddata = (
            int.from_bytes(bytestr, ENDI) & int.from_bytes(bytecomp, ENDI)
        ).to_bytes((len(bytestr)), ENDI)



# class for turf packet interface, bytes object is created at initialization, 4 bytes long only or else 4 bytes of all 0.
# to get just a byte from a bytes object, .,...
# eventually, need a packet class that expands on this, initializing with zero-filled bytes object of max length: bytes(MAX_LENGTH)
import socket

ADDR_C = b"\x0F\xFF\xFF\xFF"  # this is a bytes class
ADDR_bytearray = 0x0FFFFFFF  # this is a bytes ARRAY
TAG_C = b"\xF0\x00\x00\x00"  # this is a bytes class
TAG_bytearray = 0b11110000  # this is a bytes array
# 2 byte ascii are b'Tr' and b'Tw' respectively, these are ports (note difference to addresses in a packet which is sent to a port)
UDP_RD = b"\x54\x72"  # this is in hex, instead decimal: 21618 # obviously for reads
UDP_WR = b"\x54\x77"  # this is in hex, instead decimal: 21623 # obviously for writes
# listen for return packets on the b'Tx' port.
UDP_TX = b"Tx"  # in hex would be: 0x5478, instead decimal: 21,624
ENDI = "little"
UDP_IP = "127.0.0.2"

class packet:
    def __init__(
        self, hdr, data=[]
    ):  # default data to empty list, so its a read by default
        # methods for header
        if len(hdr) == 4:  # 32 bit "hdr" 28 bit address and 4 bit tag
            self.hdr = hdr
            self.is_badPacket = False
        else:
            self.is_badPacket = True
        if len(data) == 4:  # 32-bits of data per write?
            self.data = data
            self.is_read = False
        else:  # if not 32 bits in data, then default to a read
            self.data = []
            self.is_read = True
        if self.is_badPacket is False:
            self.address = (
                int.from_bytes(self.hdr, ENDI) & int.from_bytes(ADDR_C, ENDI)
            ).to_bytes(max(len(self.hdr), len(ADDR_C)), ENDI)
            self.tag = (
                int.from_bytes(self.hdr, ENDI) & int.from_bytes(TAG_C, ENDI)
            ).to_bytes(max(len(self.hdr), len(TAG_C)), ENDI)

            self.tag4bit = self.tag[0] & TAG_bytearray

            self.addr28bit = (
                ((self.address[0] & int.from_bytes(b"\x0F", ENDI)) << 24)
                | (self.address[1] << 16)
                | (self.address[2] << 8)
                | self.address[3]
            ) & ADDR_bytearray

            if self.is_read is False:
                self.send_write()
            else:
                self.send_read()

    def print_all(self):
        if self.is_badPacket is True:
            print("Bad packet format")
        else:
            if self.is_read is False:
                print(
                    "hdr is : x{} \t addr is: x{} \t tag is: x{} \t data is: {}".format(
                        self.hdr.hex("x"),
                        self.address.hex("x"),
                        self.tag.hex("x"),
                        self.data.hex("x"),
                    )
                )
            else:
                print(
                    "hdr is : x{} \t addr is: x{} \t tag is: x{} \t data is: {}".format(
                        self.hdr.hex("x"),
                        self.address.hex("x"),
                        self.tag.hex("x"),
                        self.data,
                    )
                )

    def send_read(self):
        # place holder print of what should be happening once port and all work
        self.sending_port = 21618

        print(
            "reading addr {}, and data should be empty: {}".format(
                self.address.hex("x"), self.data
            )
        )

    def send_write(self):
        self.sending_port = 21623
        self.connect()

        # place holder print of what should be happening once port and all work
        print(
            "hdr is : x{} \t addr is: x{} \t tag is: x{}".format(
                self.hdr.hex("x"), self.address.hex("x"), self.tag.hex("x")
            )
        )
        print(
            "writing addr {}, with data: {}".format(
                self.address.hex("x"), self.data.hex("x")
            )
        )
        print("Received: {}".format(self.ack))

    def connect(self): 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((UDP_IP, self.sending_port))
            s.sendto(self.hdr, (UDP_IP, self.sending_port))
            self.ack = s.recv(1024)
            self.ack = self.ack.decode("utf-8")

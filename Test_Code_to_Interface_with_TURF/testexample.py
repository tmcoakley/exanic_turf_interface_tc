from sfc_interface_udp import Packet
from turf_data_intepreter import packetparser as ppar

# INTERFACE IP AND PORT
MY_IP = "127.0.0.1"
MY_PORT = 21347


packet = Packet(MY_IP, MY_PORT)
#packet.write(b"\x10\x55\x00\x01\x10\x00\x00\x01")
#packet.print_ack()

bytesReturn = packet.read(b"\x20\x00\x00\x01")
print(bytesReturn)
ppar(packet.datarecd, packet.tagrecd, packet.addrrecd)
print('NEW', packet.newtag)
packet.print_ack()
#print()
# bytesReturn = packet.read(b"\x10\x00\x00\x01")
# print(bytesReturn.hex('x'))
#ppar(packet.datarecd, packet.tagrecd, packet.addrrecd)
#packet.print_ack()

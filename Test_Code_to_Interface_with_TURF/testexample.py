from sfc_interface_udp import packet
from turf_data_intepreter import packetparser as ppar

#packet = packet()
#packet.write(b"\x10\x55\x00\x01\x10\x00\x00\x01")
#packet.print_ack()

packet.read(b"\x10\x00\x00\x00")
ppar(packet.datarecd, packet.tagrecd, packet.addrrecd)
packet.print_ack()

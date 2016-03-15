import socket


class Client:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', 54545))

    def receive_ip(self):
        address, address_port_tuple = self.__socket.recvfrom(15)
        address = address.decode('utf8')
        if address == address_port_tuple[0]:
            return address

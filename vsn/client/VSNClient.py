import logging

from vsn.connectivity import client


class VSNClient(client.TCPClient):
    def __init__(self, server_address: str, server_port: int, packet_router):
        self.__packet_router = packet_router

        super().__init__(server_address, server_port)

    def connection_made(self):
        logging.info('Connection made')

    def connection_lost(self, deliberate: bool):
        if not deliberate:
            logging.error('Connection lost')
        else:
            logging.info('Disconnected')

        self._loop.stop()

    def data_received(self, received_object: object):
        self.__packet_router.route_packet(received_object)

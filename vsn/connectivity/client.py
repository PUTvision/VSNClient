import asyncio
import pickle

from abc import ABCMeta, abstractmethod


class TCPClient(metaclass=ABCMeta):
    def __init__(self, server_address: str, server_port: int):
        self.__reader, self.__writer = None, None
        self._loop = asyncio.get_event_loop()
        self._loop.run_until_complete(self.__connect(server_address, server_port))
        self.__listening_task = self._loop.create_task(self.__receive())

    def __del__(self):
        if self.__writer is not None:
            self.disconnect()

    @asyncio.coroutine
    def __connect(self, address: str, port: int):
        self.__reader, self.__writer = yield from asyncio.open_connection(address, port, loop=self._loop)
        self.connection_made()

    @asyncio.coroutine
    def __send(self, obj: object):
        encoded_data = pickle.dumps(obj)
        self.__writer.write(len(encoded_data).to_bytes(4, byteorder='big') + encoded_data)

        try:
            yield from self.__writer.drain()
        except ConnectionResetError:
            self.connection_lost(deliberate=False)

    @asyncio.coroutine
    def __receive(self):
        try:
            while True:
                encoded_length = yield from self.__reader.readexactly(4)
                length = int.from_bytes(encoded_length, byteorder='big')

                pickled_obj = yield from self.__reader.readexactly(length)
                obj = pickle.loads(pickled_obj)
                self.data_received(obj)
        except asyncio.streams.IncompleteReadError:
            self.connection_lost(deliberate=False)
        except asyncio.CancelledError:
            self.connection_lost(deliberate=True)

    def send(self, object_to_send: object):
        self._loop.create_task(self.__send(object_to_send))

    def disconnect(self):
        self.__writer.close()
        self.__listening_task.cancel()

    @abstractmethod
    def connection_made(self):
        ...

    @abstractmethod
    def connection_lost(self, deliberate):
        ...

    @abstractmethod
    def data_received(self, received_object: object):
        ...

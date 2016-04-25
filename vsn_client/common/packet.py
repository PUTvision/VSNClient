from typing import Dict, Any


class ConfigurationPacket(dict):
    def __init__(self, node_id: int, software_version: str):
        super().__init__()

        self['_pktype'] = 'svconf'
        self['node_id'] = node_id
        self['software_version'] = software_version


class DataPacket(dict):
    def __init__(self, white_pixels: float, activation_level: float,
                 gain: float, sample_time: float, image=None):
        super().__init__()

        self['_pktype'] = 'svdata'
        self['white_pixels'] = white_pixels
        self['activation_level'] = activation_level
        self['gain'] = gain
        self['sample_time'] = sample_time
        self['image'] = image


class PacketRouter:
    def __init__(self, data_packet_callback: callable([Dict[str, Any]]),
                 configuration_packet_callback: callable([Dict[str, Any]])):
        self.__data_packet_callback = data_packet_callback
        self.__configuration_packet_callback = configuration_packet_callback

    def route_packet(self, packet: Dict[str, Any]):
        print(packet)
        if packet['_pktype'] == 'cldata':
            self.__data_packet_callback(packet)
        elif packet['_pktype'] == 'clconf':
            self.__configuration_packet_callback(packet)
        else:
            raise TypeError('Packet of unsupported type received')

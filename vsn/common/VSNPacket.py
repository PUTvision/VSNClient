from vsn.common.VSNUtility import Config


class ConfigurationPacketToClient:
    def __init__(self, node_id: int=None, send_image=None, image_type=None, pkgs_to_update: list=None):
        self.node_id = node_id
        self.image_type = image_type
        self.send_image = send_image
        self.pkgs_to_update = pkgs_to_update
        self.hostname_based_ids = Config.settings['clients']['hostname_based_ids']
        self.image_size = Config.settings['clients']['image_size']
        self.frame_rate = Config.settings['clients']['frame_rate']
        self.parameters_below_threshold = Config.settings['clients']['parameters_below_threshold']
        self.parameters_above_threshold = Config.settings['clients']['parameters_above_threshold']
        self.activation_level_threshold = Config.settings['clients']['activation_level_threshold']


class ConfigurationPacketToServer:
    def __init__(self, node_id: int, software_version: str):
        self.node_id = node_id
        self.software_version = software_version


class DataPacketToServer:
    def __init__(self, white_pixels: float, activation_level: float, gain: float, sample_time: float, image=None):
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.gain = gain
        self.sample_time = sample_time
        self.image = image


class DataPacketToClient:
    def __init__(self, activation_neighbours):
        self.activation_neighbours = activation_neighbours

    def set(self, activation_neighbours):
        self.activation_neighbours = activation_neighbours


class ClientPacketRouter:
    def __init__(self, data_packet_callback: callable([object]), configuration_packet_callback: callable([object]),
                 disconnect_packet_callback: callable([object])):
        self.__data_packet_callback = data_packet_callback
        self.__configuration_packet_callback = configuration_packet_callback
        self.__disconnect_packet_callback = disconnect_packet_callback

    def route_packet(self, packet: object):
        if isinstance(packet, DataPacketToClient):
            self.__data_packet_callback(packet)
        elif isinstance(packet, ConfigurationPacketToClient):
            self.__configuration_packet_callback(packet)
        elif isinstance(packet, DisconnectPacket):
            self.__disconnect_packet_callback(packet)
        else:
            raise TypeError('Packet of unsupported type received')


class ServerPacketRouter:
    def __init__(self, data_packet_callback: callable([object, object]),
                 configuration_packet_callback: callable([object, object])):
        self.__data_packet_callback = data_packet_callback
        self.__configuration_packet_callback = configuration_packet_callback

    def route_packet(self, client, packet: object):
        if isinstance(packet, DataPacketToServer):
            self.__data_packet_callback(client, packet)
        elif isinstance(packet, ConfigurationPacketToServer):
            self.__configuration_packet_callback(client, packet)
        else:
            raise TypeError('Packet of unsupported type received')


class DisconnectPacket:
    pass

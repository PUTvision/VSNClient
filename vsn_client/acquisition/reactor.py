import asyncio
import cv2
import logging
import socket
import time

import numpy

from vsn_client import __version__
from vsn_client.common.packet import DataPacketToServer, ClientPacketRouter, ConfigurationPacketToServer
from vsn_client.common.utility import ImageType
from vsn_client.connectivity import multicast
from vsn_client.connectivity.client import VSNClient
from vsn_client.processing.activity import VSNActivityController
from vsn_client.processing.image import VSNImageProcessor


class VSNReactor:
    def __init__(self, camera):
        self.__node_id = None
        self.__camera = camera
        self.__send_image = False  # Default behavior - do not send the image data
        self.__image_type = ImageType.foreground

        self.__client = VSNClient(multicast.Client().receive_ip(),
                                  50001,
                                  ClientPacketRouter(self.__process_data_packet, self.__process_configuration_packet,
                                                     self.__process_disconnect_packet))

        self.__image_processor = VSNImageProcessor(camera.grab_image())
        self.__activity_controller = None

        self.__update_task = None
        self.__do_regular_update_time = 0

        self.__event_loop = asyncio.get_event_loop()

        self.__waiting_for_configuration = False

    def __do_regular_update(self):
        current_time = time.perf_counter()
        logging.debug('\nPREVIOUS REGULAR UPDATE WAS %.2f ms AGO' %
                      ((current_time - self.__do_regular_update_time) * 1000))
        self.__do_regular_update_time = current_time

        # Queue the next call
        self.__update_task = self.__event_loop.call_later(self.__activity_controller.sample_time,
                                                          self.__do_regular_update)

        time_start = time.perf_counter()

        percentage_of_active_pixels = self.__image_processor.get_percentage_of_active_pixels_in_frame(
            self.__camera.grab_image(slow_mode=self.__activity_controller.activation_is_below_threshold))
        self.__activity_controller.update_sensor_state_based_on_captured_image(percentage_of_active_pixels)

        time_after_get_percentage = time.perf_counter()

        if self.__activity_controller.activation_is_below_threshold and not self.__send_image:
            image_as_string = None
        else:
            image_as_string = self.__encode_image_for_sending()

        time_after_encoding = time.perf_counter()

        self.__client.send(DataPacketToServer(percentage_of_active_pixels,
                                              self.__activity_controller.activation_level,
                                              self.__activity_controller.gain,
                                              self.__activity_controller.sample_time,
                                              image_as_string))

        time_after_sending_packet = time.perf_counter()

        logging.debug('Calculating percentage took: %.2f ms' % ((time_after_get_percentage - time_start) * 1000))
        logging.debug('Encoding took: %.2f ms' % ((time_after_encoding - time_after_get_percentage) * 1000))
        logging.debug('Sending packet took: %.2f ms' % ((time_after_sending_packet - time_after_encoding) * 1000))

    def __encode_image_for_sending(self):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        image_to_send = self.__image_processor.get_image(self.__image_type)
        result, image_encoded = cv2.imencode('.jpg', image_to_send, encode_param)
        data = numpy.array(image_encoded)
        image_as_string = data.tostring()
        return image_as_string

    def __process_data_packet(self, packet):
        logging.debug('Received neighbour activation: %.2f' % packet.activation_neighbours)

        self.__activity_controller.set_params(
            activation_neighbours=packet.activation_neighbours
        )

    def __process_configuration_packet(self, packet):
        logging.info('Received configuration packet; node_id: %r; send_image: %r; image_type: %r' % (packet.node_id,
                                                                                                     packet.send_image,
                                                                                                     packet.image_type))

        self.__activity_controller = VSNActivityController(packet.parameters_below_threshold,
                                                           packet.parameters_above_threshold,
                                                           packet.activation_level_threshold)
        if packet.node_id is not None:
            # First configuration packet with node_id
            self.__node_id = packet.node_id
            self.__client.send(ConfigurationPacketToServer(self.__node_id, __version__))
        elif self.__node_id is None and packet.hostname_based_ids:
            # First configuration packet without node_id
            try:
                self.__node_id = int(''.join(x for x in socket.gethostname() if x.isdigit()))
                self.__client.send(ConfigurationPacketToServer(self.__node_id, __version__))
            except ValueError:
                logging.critical('Client hostname does not provide camera number - exiting')
                self.__client.disconnect()

        if self.__waiting_for_configuration:
            self.start()

        if packet.image_type is not None:
            self.__image_type = packet.image_type

        if packet.send_image is not None:
            self.__send_image = packet.send_image

    def __process_disconnect_packet(self, packet):
        self.__update_task.cancel()
        self.__client.disconnect()

    def start(self):
        if self.__node_id is not None:
            self.__waiting_for_configuration = False
            self.__update_task = self.__event_loop.call_later(self.__activity_controller.sample_time,
                                                              self.__do_regular_update)
        else:
            self.__waiting_for_configuration = True

        if not self.__event_loop.is_running():
            try:
                self.__event_loop.run_forever()
            except KeyboardInterrupt:
                exit(0)
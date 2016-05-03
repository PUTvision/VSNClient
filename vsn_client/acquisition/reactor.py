import asyncio
import logging
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Dict

import cv2
import numpy

from vsn_client import __version__
from vsn_client.common.packet import DataPacket, PacketRouter, \
    ConfigurationPacket
from vsn_client.common.utility import ImageType, Config
from vsn_client.connectivity.client import VSNClient
from vsn_client.processing.activity import VSNActivityController
from vsn_client.processing.image import VSNImageProcessor


class VSNReactor:
    def __init__(self, camera, server_address: str, standalone_mode=False):
        self.__node_id = None
        self.__camera = camera
        self.__send_image = False  # Default - do not send the image data
        self.__image_type = ImageType.foreground

        self.__image_processor = VSNImageProcessor(camera.grab_image())
        self.__activity_controller = None

        self.__update_task = None
        self.__do_regular_update_time = 0

        self.__event_loop = asyncio.get_event_loop()
        self.__stopped = False
        self.__executor = ThreadPoolExecutor()

        if standalone_mode:
            self.__client = None
            self.__activity_controller = VSNActivityController(
                Config.parameters_below_threshold,
                Config.parameters_above_threshold,
                Config.activation_threshold
            )

            self.start = self.__start_standalone
        else:
            self.__client = VSNClient(server_address,
                                      50001,
                                      PacketRouter(
                                          self.__process_data_packet,
                                          self.__process_configuration_packet
                                      ))
            self.__waiting_for_configuration = False

            self.start = self.__start

    async def __update(self):
        current_time = time.perf_counter()
        logging.debug('\nPREVIOUS REGULAR UPDATE WAS %.2f ms AGO' %
                      ((current_time - self.__do_regular_update_time) * 1000))
        self.__do_regular_update_time = current_time

        frame = self.__camera.grab_image(
            slow_mode=self.__activity_controller.activation_is_below_threshold
        )

        time_start = time.perf_counter()

        percentage_of_active_pixels = await self.__event_loop.run_in_executor(
            self.__executor,
            self.__image_processor.get_percentage_of_active_pixels_in_frame,
            frame
        )

        self.__activity_controller.update_sensor_state(
            percentage_of_active_pixels
        )

        time_after_get_percentage = time.perf_counter()

        if self.__activity_controller.activation_is_below_threshold \
                and not self.__send_image:
            image_as_string = None
        else:
            image_as_string = self.__encode_image_for_sending()

        time_after_encoding = time.perf_counter()

        if self.__client:
            self.__client.send(
                DataPacket(percentage_of_active_pixels,
                           self.__activity_controller.activation_level,
                           self.__activity_controller.gain,
                           self.__activity_controller.sample_time,
                           image_as_string)
            )

        time_after_sending_packet = time.perf_counter()

        logging.debug(
            'Calculating percentage took: %.2f ms' %
            ((time_after_get_percentage - time_start) * 1000)
        )
        logging.debug(
            'Encoding took: %.2f ms' %
            ((time_after_encoding - time_after_get_percentage) * 1000)
        )
        logging.debug(
            'Sending packet took: %.2f ms' %
            ((time_after_sending_packet - time_after_encoding) * 1000)
        )
        logging.debug(
            'Percentage of active pixels: %.2f' % percentage_of_active_pixels
        )

    def __encode_image_for_sending(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        image_to_send = self.__image_processor.get_image(self.__image_type)
        result, image_encoded = cv2.imencode('.jpg', image_to_send,
                                             encode_param)
        data = numpy.array(image_encoded)
        image_as_string = data.tostring()
        return image_as_string

    def __process_data_packet(self, packet):
        logging.debug('Received neighbour activation: %.2f'
                      % packet['activation_neighbours'])

        self.__activity_controller.set_params(
            activation_neighbours=packet['activation_neighbours']
        )

    def __process_configuration_packet(self, packet: Dict[str, Any]):
        logging.info('Received configuration packet;'
                     ' node_id: %r; send_image: %r; image_type: %r' %
                     (packet['node_id'],
                      packet['send_image'],
                      packet['image_type']))

        self.__activity_controller = VSNActivityController(
            packet['parameters_below_threshold'],
            packet['parameters_above_threshold'],
            packet['activation_threshold']
        )

        if self.__node_id is None:
            # Identify with hostname
            self.__node_id = socket.gethostname()
            self.__client.send(ConfigurationPacket(self.__node_id,
                                                   __version__))

        if self.__waiting_for_configuration:
            self.__event_loop.create_task(self.__run())

        if packet['image_type'] is not None:
            self.__image_type = packet['image_type']

        if packet['send_image'] is not None:
            self.__send_image = packet['send_image']

    async def __run(self):
        while not self.__stopped:
            time_start = time.perf_counter()
            await self.__update()
            time_end = time.perf_counter()

            await asyncio.sleep(
                self.__activity_controller.sample_time - (time_end - time_start)
            )

    def __start(self):
        if self.__node_id is not None:
            self.__waiting_for_configuration = False
            self.__event_loop.create_task(self.__run())
        else:
            self.__waiting_for_configuration = True

        try:
            self.__event_loop.run_forever()
        except KeyboardInterrupt:
            self.__stopped = True

    def __start_standalone(self):
        try:
            self.__event_loop.run_until_complete(self.__run())
        except KeyboardInterrupt:
            self.__stopped = True

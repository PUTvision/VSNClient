import time
import logging
from abc import ABCMeta, abstractmethod
from threading import Thread
from subprocess import check_call, CalledProcessError

import cv2

from vsn_client.common.utility import Config


class VSNCamera(metaclass=ABCMeta):
    @abstractmethod
    def grab_image(self, slow_mode=False):
        ...


class VSNCVCamera(VSNCamera):
    def __init__(self, camera_number: int):
        self.__camera = cv2.VideoCapture(camera_number)
        self.__camera.set(cv2.CAP_PROP_FRAME_WIDTH,
                          Config.image_size['width'])
        self.__camera.set(cv2.CAP_PROP_FRAME_HEIGHT,
                          Config.image_size['height'])
        logging.info('Width: {}'.format(
            self.__camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
        logging.info('Height: {}'.format(
            self.__camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # OpenCV support for setting v4l2 controls is broken
        try:
            check_call(['v4l2-ctl', '-c', 'exposure_auto=1'])  # Some web cams
        except CalledProcessError:
            logging.warning('Device does not provide exposure_auto control')

        try:
            check_call(['v4l2-ctl', '-c', 'auto_exposure=1'])  # For RPi camera
        except CalledProcessError:
            logging.warning('Device does not provide auto_exposure control')

    def grab_image(self, slow_mode=False):
        if slow_mode:
            # 5 frames buffer workaround
            for _ in range(0, 5):
                self.__camera.grab()
        else:
            self.__camera.grab()

        return self.__camera.retrieve()[1]


class VSNPiCamera(VSNCamera):
    def __init__(self):
        import picamera
        import picamera.array

        self.__camera = picamera.PiCamera()

        time.sleep(2)  # Let the camera adjust parameters in auto mode
        awb_gains = self.__camera.awb_gains
        self.__camera.awb_mode = 'off'
        self.__camera.awb_gains = awb_gains
        self.__camera.exposure_mode = 'off'

        self.__camera.resolution = (Config.image_size['width'],
                                    Config.image_size['height'])
        self.__camera.framerate = Config.frame_rate
        self.__stream = picamera.array.PiRGBArray(
            self.__camera,
            size=(Config.image_size['width'],
                  Config.image_size['height'])
        )
        self.__current_capture_thread = None

        self.__camera.capture(self.__stream, format='bgr', use_video_port=True)

    def __grab_image(self):
        self.__stream.truncate(0)
        self.__camera.capture(self.__stream, format='bgr', use_video_port=True)

    def grab_image(self, slow_mode=False):
        try:
            self.__current_capture_thread.join()
        except AttributeError:
            pass

        self.__current_capture_thread = Thread(target=self.__grab_image)
        self.__current_capture_thread.start()
        return self.__stream.array


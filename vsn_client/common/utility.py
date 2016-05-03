from collections import namedtuple
from enum import Enum


class ConfigMeta(type):
    def __getitem__(self, name):
        raise RuntimeError()

    def __setitem__(self, key, value):
        raise RuntimeError()


class Config(metaclass=ConfigMeta):
    __configuration_changed_callbacks = []

    image_size = {
        'width': 320,
        'height': 240
    }

    frame_rate = 20

    parameters_below_threshold = {
        'gain': 2,
        'sample_time': 1
    }
    parameters_above_threshold = {
        'gain': 0.1,
        'sample_time': 0.1
    }
    activation_threshold = 15

    dependencies = {}

    @classmethod
    def __execute_callbacks(cls):
        for callback in cls.__configuration_changed_callbacks:
            callback()

    @classmethod
    def add_configuration_changed_callback(cls, func: callable([])):
        cls.__configuration_changed_callbacks.append(func)

    @classmethod
    def get_dependency_value(cls, camera_id: int, neighbour_id: int) -> float:
        return cls.dependencies[camera_id][neighbour_id - 1]


GainSampletimeTuple = namedtuple('GainSampletimeTuple', ['gain', 'sample_time'])


class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'

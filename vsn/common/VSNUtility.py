import os
import sys
from enum import Enum
from collections import namedtuple

import yaml

from vsn.common.decorators import autoinitialized


@autoinitialized
class Config:
    __configuration_changed_callbacks = []
    __config_file_location = None
    settings = {}

    @classmethod
    def __execute_callbacks(cls):
        for callback in cls.__configuration_changed_callbacks:
            callback()

    @classmethod
    def initialize(cls):
        for loc in '../' + os.curdir, os.path.expanduser('~/.config/vsn'), '/etc/vsn':
            try:
                with open(os.path.join(loc, 'vsn_config.yml')) as stream:
                    for key, value in yaml.load(stream).items():
                        cls.settings[key] = value

                cls.__config_file_location = loc
                return
            except IOError:
                pass
        sys.exit('Could not find configuration file')

    @classmethod
    def set_settings(cls, gain_below_threshold: float, sample_time_below_threshold: float,
                     gain_above_threshold: float, sample_time_above_threshold: float,
                     activation_level_threshold: float, dependency_table: dict):
        cls.settings['clients']['parameters_below_threshold']['gain'] = gain_below_threshold
        cls.settings['clients']['parameters_below_threshold']['sample_time'] = sample_time_below_threshold
        cls.settings['clients']['parameters_above_threshold']['gain'] = gain_above_threshold
        cls.settings['clients']['parameters_above_threshold']['sample_time'] = sample_time_above_threshold
        cls.settings['clients']['activation_level_threshold'] = activation_level_threshold

        for camera_id, dependencies in dependency_table.items():
            for neighbour_id, dependency_value in dependencies.items():
                cls.settings['dependencies'][camera_id][neighbour_id] = dependency_value

        cls.__execute_callbacks()

    @classmethod
    def add_configuration_changed_callback(cls, func: callable([])):
        cls.__configuration_changed_callbacks.append(func)

    @classmethod
    def save_settings(cls):
        try:
            with open(os.path.join(cls.__config_file_location, 'vsn_config.yml'), 'w') as stream:
                yaml.dump(cls.settings, stream)
        except Exception as e:
            print(type(e))
            print(e)

    @classmethod
    def get_dependency_value(cls, camera_id: int, neighbour_id: int) -> float:
        return cls.settings['dependencies'][camera_id][neighbour_id - 1]


GainSampletimeTuple = namedtuple('GainSampletimeTuple', ['gain', 'sample_time'])

CameraStatisticsTuple = namedtuple('CameraStatisticsTuple', ['active_pixels', 'activity_level', 'neighbours_activation',
                                   'gain', 'sample_time', 'low_power_ticks', 'normal_ticks'])


class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'

import os
import sys
from enum import Enum
from collections import namedtuple

import yaml

from vsn_client.common.decorators import autoinitialized


class ConfigMeta(type):
    def __getitem__(self, name):
        return self._settings[name]

    def __setitem__(self, key, value):
        self._settings[key] = value


@autoinitialized
class Config(metaclass=ConfigMeta):
    __configuration_changed_callbacks = []
    __config_file_location = None
    _settings = {}

    @classmethod
    def __execute_callbacks(cls):
        for callback in cls.__configuration_changed_callbacks:
            callback()

    @classmethod
    def initialize(cls):
        for loc in (os.pardir, os.path.expanduser('~/.config/vsn_client'),
                    '/etc/vsn_client'):
            try:
                with open(os.path.join(loc, 'vsn_config.yml')) as stream:
                    for key, value in yaml.load(stream).items():
                        cls._settings[key] = value

                cls.__config_file_location = loc
                return
            except IOError:
                pass
        sys.exit('Could not find configuration file')

    @classmethod
    def set_settings(cls, gain_below_threshold: float,
                     sample_time_below_threshold: float,
                     gain_above_threshold: float,
                     sample_time_above_threshold: float,
                     activation_level_threshold: float, dependency_table: dict):
        clients = cls['clients']
        parameters_below_threshold = clients['parameters_below_threshold']
        parameters_above_threshold = clients['parameters_above_threshold']

        parameters_below_threshold['gain'] = gain_below_threshold
        parameters_below_threshold['sample_time'] = sample_time_below_threshold
        parameters_above_threshold['gain'] = gain_above_threshold
        parameters_above_threshold['sample_time'] = sample_time_above_threshold
        clients['activation_level_threshold'] = activation_level_threshold

        for camera_id, dependencies in dependency_table.items():
            for neighbour_id, dependency_value in dependencies.items():
                cls['dependencies'][camera_id][neighbour_id] = dependency_value

        cls.__execute_callbacks()

    @classmethod
    def add_configuration_changed_callback(cls, func: callable([])):
        cls.__configuration_changed_callbacks.append(func)

    @classmethod
    def save_settings(cls):
        try:
            with open(os.path.join(cls.__config_file_location,
                                   'vsn_config.yml'), 'w') as stream:
                yaml.dump(cls._settings, stream)
        except Exception as e:
            print(type(e))
            print(e)

    @classmethod
    def get_dependency_value(cls, camera_id: int, neighbour_id: int) -> float:
        return cls._settings['dependencies'][camera_id][neighbour_id - 1]


GainSampletimeTuple = namedtuple('GainSampletimeTuple', ['gain', 'sample_time'])


class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'

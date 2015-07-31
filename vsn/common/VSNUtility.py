import os
import sys
from enum import Enum
from collections import namedtuple

import yaml

from vsn.common.decorators import autoinitialized


@autoinitialized
class Config:
    @classmethod
    def initialize(cls):
        for loc in '../' + os.curdir, os.path.expanduser('~/.config/vsn'), '/etc/vsn':
            try:
                with open(os.path.join(loc, 'vsn_config.yml')) as stream:
                    for key, value in yaml.load(stream).items():
                        setattr(cls, key, value)
                return
            except IOError:
                pass
        sys.exit('Could not find configuration file')


class GainSampletimeTuple:
    def __init__(self, gain, sample_time):
        self.gain = gain
        self.sample_time = sample_time


CameraStatistics = namedtuple('CameraStatistics', ['active_pixels', 'activity_level', 'neighbours_activation',
                                                   'gain', 'sample_time', 'low_power_ticks', 'normal_ticks'])


class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'

#!/usr/bin/env python

from setuptools import setup, find_packages

from vsn_client import __version__

setup(
    name='VSN',
    version=__version__,
    description='Client for network of smart cameras with enhanced autonomy',
    author='PUT VISION LAB',
    url='https://github.com/sepherro/cam_network',
    install_requires=['picamera', 'numpy', 'msgpack-python'],
    packages=find_packages(),
    scripts=['bin/VSNClientCV', 'bin/VSNClientPiCamera'],
)

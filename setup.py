#!/usr/bin/env python

from setuptools import setup

from vsn.common.version import __version__

with open('./requirements.txt') as requirements_txt:
    requirements = [line for line in requirements_txt]

setup(name='VSN',
      version=__version__,
      description='Network of smart cameras with enhanced autonomy',
      author='PUT VISION LAB',
      url='https://github.com/sepherro/cam_network',
      install_requires=requirements,
      packages=['vsn.server', 'vsn.client', 'vsn.common', 'vsn.connectivity'],
      scripts=['vsn/VSNClientCV', 'vsn/VSNClientPiCamera', 'vsn/VSNServer', 'vsn/VSNHistoryPlotter', 'vsn/VSNUpdater'],
      )

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='pixxio_client',
      version='0.1',
      description='PIXX!O API Python Client',
      author='Claudius Hansch',
      author_email='claudius.hansch@hoerl-im.de',
      packages=find_packages(include=["pixxio_client*"]),
      install_requires=['requests', 
                        'pytz', 
                        'python-dateutil', 
                        'requests-toolbelt',
                        'dateparser']
      )
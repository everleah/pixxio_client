# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='pixxio_client',
      version='0.4.2',
      description='PIXX!O API Python Client',
      author='Claudius Hansch',
      author_email='everleah@hansch.info',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      packages=find_packages(include=["pixxio_client*"]),
      python_requires='>=3.10',
      install_requires=['requests', 
                        'pytz', 
                        'python-dateutil', 
                        'requests-toolbelt',
                        'dateparser']
      )
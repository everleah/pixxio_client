# -*- coding: utf-8 -*-

from pathlib import Path
import re

from setuptools import setup, find_packages

README = Path(__file__).with_name('README.md').read_text(encoding='utf-8')
README = re.sub(
    r'\]\((?!https?://|#)([^)]+)\)',
    r'](https://github.com/everleah/pixxio_client/blob/main/\1)',
    README,
)

setup(name='pixxio_client',
      version='0.4.5',
      description='PIXX!O API Python Client',
      long_description=README,
      long_description_content_type='text/markdown',
      author='Claudius Hansch',
      author_email='everleah@hansch.info',
      license_expression='MIT',
      license_files=['LICENSE'],
      url='https://github.com/everleah/pixxio_client',
      project_urls={
          'Source': 'https://github.com/everleah/pixxio_client',
          'Documentation': 'https://github.com/everleah/pixxio_client/blob/main/docs/README.md',
          'Issues': 'https://github.com/everleah/pixxio_client/issues',
          'Changelog': 'https://github.com/everleah/pixxio_client/blob/main/CHANGELOG.md',
      },
      keywords=['pixxio', 'dam', 'digital-asset-management', 'api', 'client'],
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3 :: Only',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      packages=find_packages(include=["pixxio_client*"]),
      include_package_data=False,
      python_requires='>=3.10',
      install_requires=['requests', 
                        'pytz', 
                        'python-dateutil', 
                        'requests-toolbelt',
                        'dateparser']
      )

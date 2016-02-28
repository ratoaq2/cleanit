#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.tests')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# requirements
install_requirements = ['appdirs>=1.4.0', 'chardet>=2.3.0', 'click>=4.0', 'jsonschema>=2.5.1', 'pysrt>=1.0.1',
                        'pyyaml>=3.11']

test_requirements = ['pytest', 'pytest-pep8', 'pytest-flakes', 'pytest-cov']

dev_requirements = ['sphinx']

# package informations
with io.open('cleanit/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with io.open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

with io.open('HISTORY.rst', 'r', encoding='utf-8') as f:
    history = f.read()


setup(name='cleanit',
      version=version,
      license='Apache License 2.0',
      description='Subtitles extremely clean',
      long_description=readme + '\n\n' + history,
      keywords='subtitle subtitles clean blacklist replace',
      url='https://github.com/ratoaq2/cleanit',
      author='Rato',
      author_email='ratoaq2@gmail.com',
      packages=find_packages(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Multimedia :: Video'
      ],
      entry_points={
          'console_scripts': [
              'cleanit = cleanit.cli:cleanit'
          ]
      },
      install_requires=install_requirements,
      tests_require=test_requirements,
      extras_require={
          'tests': test_requirements,
          'dev': dev_requirements
      },
      cmdclass={'test': PyTest})

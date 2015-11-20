#!/usr/bin/env python

from distutils.core import setup

setup(name='pyweasyl',
      description='Python bindings for the Weasyl API',
      version='1.1',
      author='Rechner Fox',
      author_email='me@profoundfox.com',
      url='https://github.com/rechner/pyweasyl',
      license='LGPL 3.0',
      py_modules=['weasyl'],
      classifiers = [
          "Programming Language :: Python",
          "Programming Language :: Python :: 3"
      ])


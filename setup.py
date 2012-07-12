#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="afns",
      version='1.0',
      description="America's finest namespace",
      author='Chris Sinchok',
      author_email='csinchok@theonion.com',
      url='http://gitlab.theonion.com/afns',
      packages = find_packages(),
      include_package_data = True,
     )
#!/usr/bin/env python

from distutils.core import setup

setup(name="afns",
      version='1.0',
      description="America's finest namespace",
      author='Chris Sinchok',
      author_email='csinchok@theonion.com',
      url='http://gitlab.theonion.com/afns',
      packages=['afns', 'afns.apps', 'afns.apps.images', 'afns.apps.markdown'],
     )
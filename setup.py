#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys


name = "django-bulbs"
package = "bulbs"
description = "America's Finest Namespace"
url = "https://github.com/theonion/django-bulbs"
author = "Chris Sinchok"
author_email = "csinchok@theonion.com"
license = "BSD"
requires = [
    "Django>=1.4",
    "South==0.8.1",
    "django-betty-cropper==0.1.1",
    "django-elastimorphic==0.0.2",
    "django-json-field==0.5.5",
    "django_polymorphic==0.5.1",
    "djangorestframework==2.3.13",
    "namedentities==1.301",
    "python-dateutil==2.1",
    "pytz==2012h",
    "requests==1.1.0",
    "simplejson==3.3.0",
    "six==1.6.1",
    "thrift==0.8.0",
    "wsgiref==0.1.2",
]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, "__init__.py")).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, "__init__.py"))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, "", 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, "__init__.py"))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    args = {"version": get_version(package)}
    print "You probably want to also tag the version now:"
    print "  git tag -a %(version)s -m 'version %(version)s'" % args
    print "  git push --tags"
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=requires
)

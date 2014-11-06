#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import re
import sys


name = "django-bulbs"
package = "bulbs"
description = "America's Finest Namespace"
url = "https://github.com/theonion/django-bulbs"
author = "Chris Sinchok"
author_email = "csinchok@theonion.com"
license = "BSD"
requires = [
    "Django>=1.7",
    "South==0.8.1",
    "django-betty-cropper>=0.1.4",
    "djangorestframework==2.4.3",
    "django-elastimorphic>=0.1.6",
    "django-json-field==0.5.5",
    "djangorestframework-csv==1.3.3",
    "python-dateutil==2.1",
    "pytz==2012h",
    "requests>=1.1.0",
    "simplejson==3.3.0",
    "six==1.6.1",
    "firebase-token-generator==1.3.2",
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

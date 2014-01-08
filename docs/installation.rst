********************
Installation & Setup
********************

Installation
============
First you need to make sure to read the :doc:`requirements`. To install
django-bulbs is easy (ONCE WE PUT IT UP ON PYPI)::

    pip install django-bulbs

Or you can go to `the github page <https://github.com/theonion/django-bulbs>`_

Setup
=====

.. highlight:: python

1. Add one or more apps (``bulbs.indexable``, ``bulbs.content``, ``bulbs.images``, or ``bulbs.video``) to your ``settings.INSTALLED_APPS``.
2. Configure your ``settings``
3. If you are using the video app, you will need to sync the
   database::

    python manage.py syncdb

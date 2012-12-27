import os
import shutil
import logging
from urlparse import urlparse

from suds.client import Client

from celery.task import task
from django.conf import settings

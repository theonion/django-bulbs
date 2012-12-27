from django.db import models
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import TextInput

from bulbs.base.models import Content

admin.site.register(Content)

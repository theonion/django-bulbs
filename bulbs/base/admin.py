from django.contrib import admin
from django.contrib.contenttypes import generic

from bulbs.base.models import Content

class ContentInline(generic.GenericTabularInline):
    model = Content

#admin.site.register(Content)

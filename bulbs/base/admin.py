from django.contrib import admin
from django.contrib.contenttypes import generic

from bulbs.base.models import Content

class ContentInline(generic.GenericStackedInline):
    model = Content
    max_num = 1

admin.site.register(Content)

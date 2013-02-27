from django.contrib import admin
from django.contrib.contenttypes import generic

from bulbs.base.models import Content, Tag


class ContentInline(generic.GenericStackedInline):
    model = Content
    max_num = 1


class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type',)
    list_filter = ('content_type',)

admin.site.register(Content, ContentAdmin)
admin.site.register(Tag)

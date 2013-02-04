from django.contrib import admin
from django.contrib.contenttypes import generic

from bulbs.base.models import Handle, Tag


class HandleInline(generic.GenericStackedInline):
    model = Handle
    max_num = 1


class HandleAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type',)
    list_filter = ('content_type',)

admin.site.register(Handle, HandleAdmin)
admin.site.register(Tag)

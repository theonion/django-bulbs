from django.db import models
from django.contrib import admin

from bulbs.base.admin import ContentInline
from bulbs.videos.models import Video, VideoSource
from bulbs.videos.widgets import AmazonUploadWidget


class VideoSourceInline(admin.StackedInline):
    model = VideoSource


class VideoAdmin(admin.ModelAdmin):
    inlines = [VideoSourceInline]
    formfield_overrides = {
        models.URLField: {'widget': AmazonUploadWidget}
    }
    inlines = [
        ContentInline,
    ]

admin.site.register(Video, VideoAdmin)

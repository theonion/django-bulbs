from django.contrib import admin
from django.forms import TextInput

from bulbs.images.models import Image, ImageAspectRatio, ImageSelection

admin.site.register(Image)
admin.site.register(ImageAspectRatio)
admin.site.register(ImageSelection)

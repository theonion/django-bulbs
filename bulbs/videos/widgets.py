from django import forms
from django.contrib.admin.templatetags.admin_static import static


class AmazonUploadWidget(forms.ClearableFileInput):

    @property
    def media(self):
        js = ["uploader.js"]
        return forms.Media(js=[static("videos/js/%s" % path) for path in js])

from django import forms
from django.forms.util import flatatt
from django.contrib.admin.templatetags.admin_static import static
from django.utils.html import escape, conditional_escape
from django.utils.translation import ugettext_lazy
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class AmazonUploadWidget(forms.ClearableFileInput):

    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    template = '<span class="initial" %(initial_extras)s><input %(initial)s/> <a href="#" class="video-choose">Choose New Video</a> </span>\
        <span class="upload" %(upload_extras)s>%(input)s <a class="video-upload" href="#upload" data-url="https://onionwebtech.s3.amazonaws.com" >Upload Video</a><a class="video-upload-close" href="#">Close</a></span>'


    class Media:
        js = (static('videos/js/uploader.js'))
        css = {'all': [static('videos/css/admin.css')]}

    @property
    def media(self):
        js = [static('videos/js/uploader.js'), reverse('bulbs.videos.views.aws_attrs')]
        css = {'all': [static('videos/css/admin.css')]}
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'initial': self.build_attrs({
                'class':"vURLField",
                'value': escape(value) if value else '',
                'name': name,
                'type': 'text',
                'id': 'id_%s' % name
            }),
            "initial_extras": "",
            "upload_extras": ""
        }
        
        if value:
            substitutions['upload_extras'] = "style='display:none;'"
        else:
            substitutions['initial_extras'] = "style='display:none;'"
        
        template = self.template
        substitutions['input'] = super(AmazonUploadWidget, self).render(name, value, attrs)
        substitutions['initial'] = flatatt(substitutions['initial'])

        return mark_safe(template % substitutions)
        
    def value_from_datadict(self, data, files, name):
        # default file behavior is to grab value from
        # files
        return data.get(name, None)

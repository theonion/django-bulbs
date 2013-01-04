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
    template_with_initial = '<a href="%(initial)s">%(initial)s</a> %(blank_template)s <a href="#">Choose New Video</a>'
    blank_template = '%(input)s <a class="video-upload" href="#upload" data-url="https://onionwebtech.s3.amazonaws.com" >Upload Video</a>'


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
            'extras': {}
        }
        
        template = self.blank_template
        substitutions['input'] = super(AmazonUploadWidget, self).render(name, value, attrs)
                
        if value:
            template = self.template_with_initial
            substitutions['initial'] = escape(value)
            substitutions['extras']['style'] = "display:none;"
            substitutions['blank_template'] = self.blank_template % substitutions

        substitutions['extras'] = flatatt(substitutions['extras'])
        return mark_safe(template % substitutions)
        
    def value_from_datadict(self, data, files, name):
        # default file behavior is to grab value from
        # files
        return data.get(name, None)

from django import forms
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import ugettext_lazy
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class AmazonUploadWidget(forms.FileInput):

    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    template_with_initial = '%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s <a class="video-upload" href="#upload">Upload Video</a>'

    class Media:
        js = (static('videos/js/uploader.js'))

    @property
    def media(self):
        js = [static('videos/js/uploader.js'), reverse('bulbs.videos.views.aws_attrs')]
        return forms.Media(js=js)

    def render(self, name, value, attrs=None):

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
        }
        template = '%(input)s <a class="video-upload" href="#upload" data-url="https://onionwebtech.s3.amazonaws.com" >Upload Video</a>'
        substitutions['input'] = super(AmazonUploadWidget, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial

        return mark_safe(template % substitutions)

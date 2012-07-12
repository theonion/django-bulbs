from django import forms
from django.conf import settings
from django.contrib.admin import widgets as admin_widgets
from django.core.urlresolvers import reverse
from django.forms.widgets import flatatt
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.forms.util import smart_unicode
from django.utils.html import escape
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext as _
from django.template.loader import render_to_string

class Markdown(forms.Textarea):

    class Media:
        js = (  'markdown/js/markdown-editor.js',
                'markdown/js/markdown.js',
                'markdown/codemirror/lib/codemirror.js',
                'markdown/codemirror/mode/xml/xml.js',
                'markdown/codemirror/mode/markdown/markdown.js',
                'markdown/codemirror/mode/htmlmixed/htmlmixed.js')
                
        css = {'screen': (  'markdown/codemirror/theme/elegant.css',
                            'markdown/codemirror/lib/codemirror.css',
                            'markdown/css/markdown-widget.css')
                }

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs)
        final_attrs['name'] = name
        if 'class' in final_attrs:
            final_attrs['class'] += ' markdown-editor'
        else:
            final_attrs['class'] = 'markdown-editor'
        assert 'id' in final_attrs, "Markdown widget attributes must contain 'id'"

        html = render_to_string('markdown/markdown-widget.html', {  'name': name, 
                                                                    'attrs': flatatt(final_attrs), 
                                                                    'value': escape(value)})
        return html

class AdminMarkdown(admin_widgets.AdminTextareaWidget, Markdown):
    pass
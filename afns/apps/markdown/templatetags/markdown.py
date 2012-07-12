import markdown

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def markdown(value, arg=''):
    return mark_safe(markdown.markdown(force_unicode(value), ['smartypants','onion']), safe_mode=False)
from __future__ import absolute_import

from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def markdown(value, arg=''):
    try:
        from markdown import markdown as markdown_function
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'markdown' filter: The Python markdown library isn't installed.")
        return force_unicode(value)
    return mark_safe(markdown_function(force_unicode(value), ['smartypants'],  safe_mode=False))

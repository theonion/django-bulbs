import markdown

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def markdown(value, arg=''):
    try:
        import markdown
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'markdown' filter: The Python markdown library isn't installed.")
        return force_unicode(value)
    else:
        markdown_vers = getattr(markdown, "version_info", 0)
        if markdown_vers < (2, 1):
            if settings.DEBUG:
                raise template.TemplateSyntaxError(
                    "Error in 'markdown' filter: Django does not support versions of the Python markdown library < 2.1.")
            return force_unicode(value)
        else:
            return mark_safe(markdown.markdown(
                force_unicode(value), ['smartypants','onion'], safe_mode=False))
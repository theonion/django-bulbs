from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def markdown(value, arg=''):
    try:
        import markdown as markdown_lib
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'markdown' filter: The Python markdown library isn't installed.")
        return force_unicode(value)
    return mark_safe(markdown_lib.markdown(force_unicode(value), ['smartypants','onion']), safe_mode=False)

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag()
def special_coverage_landing_partial(takes_context=True):
    return render_to_string("special_coverage/landing.html")

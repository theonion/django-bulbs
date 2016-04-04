from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def special_coverage_landing_partial(context):
    return render_to_string("special_coverage/bulbs_landing.html")

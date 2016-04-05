from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.inclusion_tag('special_coverage/bulbs_sc_landing.html', takes_context=True)
def special_coverage_landing_partial(context):
    return context

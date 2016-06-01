import json

from django.template import Library, Context
from django.template.loader import get_template


register = Library()


@register.simple_tag(takes_context=True)
def ads_targeting(context):
    return get_template(
        "ads/ads-targeting.html"
    ).render(
        Context({
            "targeting": context.get("targeting")
        })
    )


@register.simple_tag
def dfp_ad(ad_unit, css_class=''):
    template = get_template("ads/dfp.html")
    context = {
        "ad_unit": ad_unit,
        "css_class": css_class
    }

    return template.render(Context(context))


@register.simple_tag(takes_context=True)
def targeting(context):
    targeting_template = "<script>var TARGETING={};</script>"  # Cute, huh?
    if "targeting" not in context:
        return targeting_template
    return targeting_template.format(json.dumps(context["targeting"]))

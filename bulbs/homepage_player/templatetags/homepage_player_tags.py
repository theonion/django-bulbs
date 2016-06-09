from django import template
from bulbs.utils.methods import get_overridable_template_name

register = template.Library()

template_name = get_overridable_template_name(
        'homepage_player/bulbs_homepage_player.html',
        'homepage_player/homepage_player_override.html',
        )


@register.inclusion_tag(template_name, takes_context=True)
def homepage_player_partial(context, videos=[]):
    context['videos'] = videos
    return context

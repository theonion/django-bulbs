from django import template

register = template.Library()


@register.inclusion_tag('homepage_player/bulbs_homepage_player.html', takes_context=True)
def homepage_player_partial(context, videos=[]):
    context['videos'] = videos
    return context

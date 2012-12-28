from django import template

register = template.Library()


@register.inclusion_tag('videos/player.html')
def player(video, width=None):
    context = {'video': video}
    if width:
        context['width'] = width
        context['height'] = int(width * .5625)
    return context

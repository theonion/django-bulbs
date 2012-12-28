from django import template

register = template.Library()


@register.inclusion_tag('videos/player.html')
def player(video, width=None, height=None):
    context = {'video': video}
    if width:
        context['width'] = width
        if height is None:
            context['height'] = int(width * 9 / 16)
    if height:
        context['height'] = height
        if width is None:
            context['width'] = int(width * 16 / 9)
    return context

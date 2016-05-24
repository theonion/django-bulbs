from django import template

register = template.Library()


@register.inclusion_tag('video-series/video-series-flyout-list.html', takes_context=True)
def video_series_flyout_list(context, channel_slug):
    context["channel_slug"] = channel_slug
    return context

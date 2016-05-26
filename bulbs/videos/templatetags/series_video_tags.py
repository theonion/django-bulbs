from django import template

register = template.Library()


@register.inclusion_tag('videos/series-video-list.html', takes_context=True)
def series_video_list(context, channel_slug):
    context["channel_slug"] = channel_slug
    return context


@register.inclusion_tag('videos/series-page.html', takes_context=True)
def series_video_page(context, series_slug):
    context["series_slug"] = series_slug
    return context

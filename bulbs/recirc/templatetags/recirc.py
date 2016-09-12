from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Library
from django.template.loader import get_template

from bulbs.content.models import Content
from bulbs.promotion.models import PZone


register = Library()


@register.simple_tag
def end_of_article_video():
    '''
    templatetag that renders the end of article video recirc.
    '''
    try:
        queryset = PZone.objects.applied(name='end-of-article-videos')
    except ObjectDoesNotExist:
        queryset = Content.search_objects.videos()

    try:
        # TODO: come up with a sane way to iterate.
        video = queryset[0]
    except IndexError:
        return

    site_name = getattr(settings, "SITE_DISPLAY_NAME", None)
    recirc_text = "Watch Video " + str(video.videohub_ref.id)
    if site_name:
        recirc_text += " From " + site_name

    base_url = getattr(settings, "VIDEOHUB_BASE_URL", None) + "/video/{}.json"
    if base_url is None:
        return ""

    return get_template(
        "recirc/end_of_article.html"
    ).render(
        Context({
            'recirc_text': recirc_text,
            'video_src': base_url.format(video.videohub_ref.id)
        })
    )

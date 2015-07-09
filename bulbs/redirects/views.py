try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from bulbs.content.models import Content

from django.http import HttpResponsePermanentRedirect
from django.views.decorators.cache import patch_cache_control
from django.template.response import TemplateResponse

utm_source = {
    "f": "facebook",
    "t": "twitter",
    "e": "email"
}

utm_medium = {
    "s": "ShareTools"
}

utm_campaign = {
    "d": "default"
}


def utm_redirect(request, pk, source=None, medium=None, name=None):
    try:
        content = Content.objects.get(pk=pk)
    except Content.DoesNotExist:
        # should really just return whatever handler404 is here
        response = TemplateResponse(request, "404.html", {}, status=404)
        patch_cache_control(response, no_cache=True)
        return response

    content_url = content.get_absolute_url()

    # UTM Tracking only works if all three are present...
    if source and medium and name:
        query_string = urlencode({
            "utm_source": utm_source.get(source, "none"),
            "utm_medium": utm_medium.get(medium, "none"),
            "utm_campaign": utm_campaign.get("utm_campaign", "default")
        })
        content_url = "{}?{}".format(content_url, query_string)

    return HttpResponsePermanentRedirect(content_url)

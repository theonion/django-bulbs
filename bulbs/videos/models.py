import json

from djes.models import Indexable

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from djbetty.fields import ImageField

import requests

import six


class VideohubVideo(Indexable):
    """A reference to a video on the onion videohub."""
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True, default="")
    keywords = models.TextField(blank=True, default="")
    image = ImageField(null=True, blank=True, alt_field="_image_alt",
                       caption_field="_image_caption")
    _image_alt = models.CharField(null=True, blank=True, editable=False, max_length=255)
    _image_caption = models.CharField(null=True, blank=True, editable=False, max_length=255)
    # External FK on videohub. Temp workaround until metadata refactor.
    channel_id = models.IntegerField(blank=True, null=True, default=None)

    # default values
    DEFAULT_VIDEOHUB_VIDEO_URL = "http://videohub.local/videos/{}"
    DEFAULT_VIDEOHUB_EMBED_URL = "http://videohub.local/embed?id={}"
    DEFAULT_VIDEOHUB_API_URL = "http://videohub.local/api/v0/videos/{}"
    DEFAULT_VIDEOHUB_API_SEARCH_URL = "http://videohub.local/api/v0/videos/search"

    class Mapping:
        class Meta:
            # Exclude image until we actually need it, to avoid dealing with custom mappings
            excludes = ('image',)

    @classmethod
    def get_serializer_class(cls):
        from .serializers import VideohubVideoSerializer
        return VideohubVideoSerializer

    @classmethod
    def search_videohub(cls, query, filters=None, status=None, sort=None, size=None, page=None):
        """searches the videohub given a query and applies given filters and other bits

        :see: https://github.com/theonion/videohub/blob/master/docs/search/post.md
        :see: https://github.com/theonion/videohub/blob/master/docs/search/get.md

        :param query: query terms to search by
        :type query: str
        :example query: "brooklyn hipsters"  # although, this is a little redundant...

        :param filters: video field value restrictions
        :type filters: dict
        :default filters: None
        :example filters: {"channel": "onion"} or {"series": "Today NOW"}

        :param status: limit the results to videos that are published, scheduled, draft
        :type status: str
        :default status: None
        :example status: "published" or "draft" or "scheduled"

        :param sort: video field related sorting
        :type sort: dict
        :default sort: None
        :example sort: {"title": "desc"} or {"description": "asc"}

        :param size: the page size (number of results)
        :type size: int
        :default size: None
        :example size": {"size": 20}

        :param page: the page number of the results
        :type page: int
        :default page: None
        :example page: {"page": 2}  # note, you should use `size` in conjunction with `page`

        :return: a dictionary of results and meta information
        :rtype: dict
        """
        # construct url
        url = getattr(settings, "VIDEOHUB_API_SEARCH_URL", cls.DEFAULT_VIDEOHUB_API_SEARCH_URL)
        # construct auth headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": settings.VIDEOHUB_API_TOKEN,
        }
        # construct payload
        payload = {
            "query": query,
        }
        if filters:
            assert isinstance(filters, dict)
            payload["filters"] = filters
        if status:
            assert isinstance(status, six.string_types)
            payload.setdefault("filters", {})
            payload["filters"]["status"] = status
        if sort:
            assert isinstance(sort, dict)
            payload["sort"] = sort
        if size:
            assert isinstance(size, (six.string_types, int))
            payload["size"] = size
        if page:
            assert isinstance(page, (six.string_types, int))
            payload["page"] = page
        # send request
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        # raise if not 200
        if res.status_code != 200:
            res.raise_for_status()
        # parse and return response
        return json.loads(res.content)

    def get_hub_url(self):
        """gets a canonical path to the detail page of the video on the hub

        :return: the path to the consumer ui detail page of the video
        :rtype: str
        """
        url = getattr(settings, "VIDEOHUB_VIDEO_URL", self.DEFAULT_VIDEOHUB_VIDEO_URL)

        # slugify needs ascii
        ascii_title = ""
        if isinstance(self.title, str):
            ascii_title = self.title
        elif six.PY2 and isinstance(self.title, six.text_type):
            # Legacy unicode conversion
            ascii_title = self.title.encode('ascii', 'replace')

        path = slugify("{}-{}".format(ascii_title, self.id))

        return url.format(path)

    def get_embed_url(self, targeting=None, recirc=None):
        """gets a canonical path to an embedded iframe of the video from the hub

        :return: the path to create an embedded iframe of the video
        :rtype: str
        """
        url = getattr(settings, "VIDEOHUB_EMBED_URL", self.DEFAULT_VIDEOHUB_EMBED_URL)
        url = url.format(self.id)
        if targeting is not None:
            for k, v in sorted(targeting.items()):
                url += '&{0}={1}'.format(k, v)
        if recirc is not None:
            url += '&recirc={0}'.format(recirc)
        return url

    def get_api_url(self):
        """gets a canonical path to the api detail url of the video on the hub

        :return: the path to the api detail of the video
        :rtype: str
        """
        url = getattr(settings, 'VIDEOHUB_API_URL', None)
        # Support alternate setting (used by most client projects)
        if not url:
            url = getattr(settings, 'VIDEOHUB_API_BASE_URL', None)
            if url:
                url = url.rstrip('/') + '/videos/{}'
        if not url:
            url = self.DEFAULT_VIDEOHUB_API_URL
        return url.format(self.id)

try:
    import json
except ImportError:
    import simplejson as json

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from djbetty import ImageField
import requests


class VideoHubVideo(models.Model):
    # fields
    id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    poster_caption = models.CharField(null=True, blank=True, max_length=255)
    poster_alt = models.CharField(null=True, blank=True, max_length=255)
    poster = ImageField(null=True, blank=True, default=None, alt_field="poster_alt", caption_field="poster_caption")

    # default values
    DEFAULT_HUB_URL_BASE = "http://videohub.local/"
    DEFAULT_HUB_LIST_VIEW = "videos/"
    DEFAULT_EMBED_URL = "embed?id="
    DEFAULT_HUB_API_URL = "api/"
    DEFAULT_HUB_API_VERSION = "v0/"
    DEFAULT_HUB_API_LIST_VIEW = "videos/"

    @classmethod
    def get_serializer_class(cls):
        from .serializers import VideoHubVideoSerializer
        return VideoHubVideoSerializer

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
        url = cls.DEFAULT_HUB_URL_BASE + cls.DEFAULT_HUB_API_URL + cls.DEFAULT_HUB_API_VERSION + \
              cls.DEFAULT_HUB_API_LIST_VIEW + "search"

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
            assert isinstance(status, basestring)
            payload.setdefault("filters", {})
            payload["filters"]["status"] = status
        if sort:
            assert isinstance(sort, dict)
            payload["sort"] = sort
        if size:
            assert isinstance(size, (basestring, int))
            payload["size"] = size
        if page:
            assert isinstance(page, (basestring, int))
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
        default = self.DEFAULT_HUB_URL_BASE + self.DEFAULT_HUB_LIST_VIEW
        url = getattr(settings, "VIDEOHUB_VIDEO_HUB_URL", default)
        if not url.endswith("/"):
            url += "/"
        detail = slugify(self.title) + "-" + str(self.id)
        return url + detail

    def get_embed_url(self):
        """gets a canonical path to an embedded iframe of the video from the hub

        :return: the path to create an embedded iframe of the video
        :rtype: str
        """
        default = self.DEFAULT_HUB_URL_BASE + self.DEFAULT_EMBED_URL
        url = getattr(settings, "VIDEOHUB_VIDEO_EMBED_URL", default)
        if not url.endswith("?id="):
            url += "?id="
        return url + str(self.id)

    def get_api_url(self):
        """gets a canonical path to the api detail url of the video on the hub

        :return: the path to the api detail of the video
        :rtype: str
        """
        default = self.DEFAULT_HUB_URL_BASE + self.DEFAULT_HUB_API_URL + self.DEFAULT_HUB_API_VERSION + \
                  self.DEFAULT_HUB_API_LIST_VIEW
        url = getattr(settings, "VIDEOHUB_VIDEO_API_URL", default)
        if not url.endswith("/"):
            url += "/"
        return url + str(self.id)

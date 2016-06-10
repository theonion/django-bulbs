#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.template.defaultfilters import slugify
from django.test import TestCase

from bulbs.videos.models import VideohubVideo
from bulbs.videos.serializers import VideohubVideoSerializer


class VideohubVideoTests(TestCase):

    def setUp(self):
        self.video = VideohubVideo.objects.create(
            id=1,
            title="Lake Dredge Appraisal Episode 2",
            description="Revolting Silt",
            keywords="Lake Dredge Appraisal Revoling Silt Episode 2"
        )

    def test_hub_url(self):
        with self.settings(VIDEOHUB_VIDEO_URL="http://onionstudios.com/video/{}"):
            hub_url = self.video.get_hub_url()
            slug = slugify(self.video.title)
            self.assertEquals(
                hub_url,
                "http://onionstudios.com/video/{}-{}".format(slug, self.video.id))

    def test_embed_url(self):
        with self.settings(VIDEOHUB_EMBED_URL="http://onionstudios.com/embed?id={}"):
            embed_url = self.video.get_embed_url()
            self.assertEquals(
                embed_url,
                "http://onionstudios.com/embed?id={}".format(self.video.id))

    def test_embed_url_with_recirc(self):
        with self.settings(VIDEOHUB_EMBED_URL="http://onionstudios.com/embed?id={}"):
            embed_url = self.video.get_embed_url(recirc=3)
            self.assertEquals(
                embed_url,
                "http://onionstudios.com/embed?id={}&recirc=3".format(self.video.id))

    def test_embed_url_with_targeting(self):
        with self.settings(VIDEOHUB_EMBED_URL="http://onionstudios.com/embed?id={}"):
            targeting = {
                'target_host_channel': 'specialcoverage',
                'target_special_coverage': 'joe-biden'
            }
            embed_url = self.video.get_embed_url(targeting=targeting)
            self.assertEquals(
                embed_url,
                ("http://onionstudios.com/embed?id={}&target_host_channel=specialcoverage"
                 "&target_special_coverage=joe-biden".format(self.video.id))
            )

    def test_api_url(self):
        with self.settings(VIDEOHUB_API_URL="http://onionstudios.com/api/v0/videos/{}"):
            api_url = self.video.get_api_url()
            self.assertEquals(
                api_url,
                "http://onionstudios.com/api/v0/videos/{}".format(self.video.id))

    def test_api_url_alternate_setting(self):
        with self.settings(VIDEOHUB_API_BASE_URL="http://onionstudios.com/api/v0/"):
            api_url = self.video.get_api_url()
            self.assertEquals(
                api_url,
                "http://onionstudios.com/api/v0/videos/{}".format(self.video.id))

    def test_serializer_has_urls(self):
        with self.settings(VIDEOHUB_VIDEO_URL="http://onionstudios.com/video/{}"), \
                self.settings(VIDEOHUB_EMBED_URL="http://onionstudios.com/embed?id={}"), \
                self.settings(VIDEOHUB_API_URL="http://onionstudios.com/api/v0/videos/{}"):
            hub_url = self.video.get_hub_url()
            embed_url = self.video.get_embed_url()
            api_url = self.video.get_api_url()
            serializer = VideohubVideoSerializer(self.video)
            self.assertEquals(hub_url, serializer.data["hub_url"])
            self.assertEquals(embed_url, serializer.data["embed_url"])
            self.assertEquals(api_url, serializer.data["api_url"])

    def test_hub_url_with_unicode(self):
        """Make sure get_hub_url can handle unicode characters properly."""

        video_1 = VideohubVideo.objects.create(title=u"\u2019The Facts Of Life\u2019")
        video_2 = VideohubVideo.objects.create(title=u"‘The Facts Of Life’")

        self.assertEqual(video_1.get_hub_url(), VideohubVideoSerializer(video_1).data["hub_url"])
        self.assertEqual(video_2.get_hub_url(), VideohubVideoSerializer(video_2).data["hub_url"])

from datetime import timedelta

from django.utils import timezone

from bulbs.content.filters import FeatureTypes
from bulbs.content.models import Content, FeatureType, Tag
from bulbs.special_coverage.search import second_slot_query_generator
from bulbs.utils.test import BaseIndexableTestCase, make_content


class SpecialCoverageSearchTests(BaseIndexableTestCase):
    """TestCase for custom special coverage test cases."""
    def setUp(self):
        super(SpecialCoverageSearchTests, self).setUp()
        feature_type_names = (
            "News", "Slideshow", "TV Club", "Video",
        )
        feature_types = []
        for name in feature_type_names:
            feature_types.append(FeatureType.objects.create(name=name))
        tag_names = (
            "Barack Obama", "Joe Biden", "Wow", "Funny", "Politics"
        )
        tags = []
        for name in tag_names:
            tags.append(Tag.objects.create(name=name))
        content_data = (
            dict(
                title="Obama Does It Again",
                feature_type=0,
                tags=[0, 2, 4]
            ),
            dict(
                title="Biden Does It Again",
                feature_type=0,
                tags=[1, 2, 4]
            ),
            dict(
                title="Obama In Slides Is Flawless",
                feature_type=1,
                tags=[0, 2, 4]
            ),
            dict(
                title="Obama On TV",
                feature_type=2,
                tags=[0, 2]
            ),
            dict(
                title="Flawless video here",
                feature_type=3,
                tags=[3, 2]
            ),
            dict(
                title="Both Obama and Biden in One Article",
                feature_type=3,
                tags=[0, 1, 2]
            ),
        )
        time_step = timedelta(hours=12)
        pubtime = timezone.now() + time_step
        content_list = []
        for data in content_data:
            data["published"] = pubtime
            data["feature_type"] = feature_types[data.pop("feature_type")]
            data["tags"] = [tags[tag_idx] for tag_idx in data.pop("tags")]
            content = make_content(**data)
            content_list.append(content)
            content.index()  # reindex for related object updates
            pubtime -= time_step
        self.content_list = content_list
        self.feature_types = feature_types
        self.tags = tags
        Content.search_objects.refresh()

    def test_second_slot_query_generator(self):
        news_search = Content.search_objects.search().filter(FeatureTypes(["news"]))
        video_search = Content.search_objects.search().filter(FeatureTypes(["video"]))
        search_party = [obj for obj in second_slot_query_generator(video_search, news_search)]
        self.assertEqual(search_party[0], video_search[0])
        self.assertEqual(search_party[1], news_search[0])
        self.assertEqual(search_party[2], video_search[1])

        tv_club_search = Content.search_objects.search().filter(FeatureTypes(["tv-club"]))
        search_party = [obj for obj in second_slot_query_generator(video_search, tv_club_search)]
        self.assertEqual(search_party[0], video_search[0])
        self.assertEqual(search_party[1], tv_club_search[0])
        self.assertEqual(search_party[2], video_search[1])

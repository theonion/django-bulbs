from datetime import timedelta

from django.utils import timezone

from bulbs.campaigns.models import Campaign
from bulbs.content.filters import FeatureTypes
from bulbs.content.models import Content, FeatureType, Tag
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.special_coverage.search import SearchParty, second_slot_query_generator
from bulbs.utils.test import BaseIndexableTestCase, make_content


class SpecialCoverageSearchTests(BaseIndexableTestCase):
    """TestCase for custom special coverage test cases."""
    def setUp(self):
        super(SpecialCoverageSearchTests, self).setUp()
        self.now = timezone.now()
        feature_type_names = (
            "News", "Slideshow", "TV Club", "Video",
        )
        feature_types = []
        for name in feature_type_names:
            feature_types.append(FeatureType.objects.create(name=name))
        tag_names = (
            "Barack Obama", "Joe Biden", "wow", "Funny", "Politics"
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
        pubtime = self.now + time_step
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

        campaign = Campaign.objects.create(
            sponsor_name="big",
            start_date=self.now - timezone.timedelta(days=5),
            end_date=self.now + timezone.timedelta(days=5)
        )

        self.special_coverages = [
            SpecialCoverage.objects.create(
                name="Slime Season",
                campaign=campaign,
                start_date=self.now - timezone.timedelta(days=10),
                end_date=self.now + timezone.timedelta(days=10),
                query={
                    "groups": [{
                        "conditions": [{
                            "field": "feature-type",
                            "type": "any",
                            "values": [{
                                "name": "news", "value": "news"
                            }]
                        }],
                        "time": None
                    }]
                }
            ),
            SpecialCoverage.objects.create(
                name="Slime Season 2",
                start_date=self.now - timezone.timedelta(days=10),
                end_date=self.now + timezone.timedelta(days=10),
                query={
                    "groups": [{
                        "conditions": [{
                            "field": "tag",
                            "type": "any",
                            "values": [{
                                "name": "wow", "value": "wow"
                            }]
                        }],
                        "time": None
                    }],
                }
            )
        ]

        Content.search_objects.refresh()

    def test_search_party_query(self):
        search_party = SearchParty(self.special_coverages)
        self.assertItemsEqual(
            search_party.query,
            {
                "excluded_ids": [],
                "included_ids": [],
                "pinned_ids": [],
                "groups": [{
                    "conditions": [{
                        "field": "feature-type",
                        "type": "any",
                        "values": [{"name": "news", "values": "news"}],
                        "time": None
                    }],
                    "conditions": [{
                        "field": "tags",
                        "type": "any",
                        "values": [{"name": "wow", "values": "wow"}],
                        "time": None
                    }]
                }]
            }
        )

    def test_search_party_search(self):
        search_party = SearchParty(self.special_coverages)
        search = search_party.search()
        # Returns all published content
        self.assertEqual(search.count(), 5)

        # Update special coverages for more unique test cases.
        sc1, sc2 = self.special_coverages[0], self.special_coverages[1]
        sc1.query = {
            "groups": [{
                "conditions": [{
                    "field": "feature-type",
                    "type": "any",
                    "values": [{
                        "name": "slideshow", "value": "slideshow"
                    }]
                }],
                "time": None
            }]
        }
        sc1.save()
        sc2.query = {
            "groups": [{
                "conditions": [{
                    "field": "tag",
                    "type": "any",
                    "values": [{
                        "name": "funny", "value": "funny"
                    }]
                }],
                "time": None
            }],
        }
        sc2.save()

        search_party = SearchParty(self.special_coverages)
        import pdb; pdb.set_trace()
        search = search_party.search()
        self.assertEqual(search.count(), 2)

    def test_second_slot_query_generator(self):
        news_search = Content.search_objects.search().filter(FeatureTypes(["news"]))
        video_search = Content.search_objects.search().filter(FeatureTypes(["video"]))
        search_party = [obj for obj in second_slot_query_generator(video_search, news_search)]
        self.assertEqual(search_party[0], video_search[0])
        self.assertEqual(search_party[1], news_search[0])
        self.assertEqual(search_party[2], video_search[1])

        video_search = Content.search_objects.search().filter(FeatureTypes(["video"]))
        tv_club_search = Content.search_objects.search().filter(FeatureTypes(["tv-club"]))
        search_party = [obj for obj in second_slot_query_generator(video_search, tv_club_search)]
        self.assertEqual(search_party[0], video_search[0])
        self.assertEqual(search_party[1], tv_club_search[0])
        self.assertEqual(search_party[2], video_search[1])

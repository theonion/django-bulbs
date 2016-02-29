from datetime import timedelta

from django.utils import timezone

from elasticsearch_dsl import filter as es_filter

from bulbs.campaigns.models import Campaign
from bulbs.content.models import Content, FeatureType, Tag
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.special_coverage.search import SearchSlicer, SearchParty
from bulbs.utils.test import BaseIndexableTestCase, make_content


class SearchSlicerTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(SearchSlicerTestCase, self).setUp()
        self.now = timezone.now()
        self.feature_type1 = FeatureType.objects.create(name="Arguments")
        self.feature_type2 = FeatureType.objects.create(name="Falling")
        for i in range(20):
            Content.objects.create(
                title="content %s" % i,
                published=self.now - timezone.timedelta(hours=i),
                feature_type=self.feature_type1
            )
            Content.objects.create(
                title="article %s" % i,
                published=self.now - timezone.timedelta(hours=i),
                feature_type=self.feature_type2
            )
        Content.search_objects.refresh()

    def test_register_queryset_default_first(self):
        queryset = Content.search_objects.search(
            feature_types=[self.feature_type1.slug]
        ).sort("id")
        reading_list = SearchSlicer()
        # First queryset should be default until explicitly state otherwise.
        reading_list.register_queryset(queryset)
        self.assertEqual(reading_list.default_queryset, queryset)
        out = [obj for obj in reading_list]
        expected_out = [obj for obj in queryset[:queryset.count()]]
        self.assertEqual(out, expected_out)

    def test_register_queryset_set_default(self):
        queryset1 = Content.search_objects.search(feature_types=[self.feature_type1.slug])
        queryset2 = Content.search_objects.search(feature_types=[self.feature_type2.slug])
        reading_list = SearchSlicer()
        reading_list.register_queryset(queryset1)
        reading_list.register_queryset(queryset2, default=True)
        self.assertEqual(reading_list.default_queryset, queryset2)

    def test_validator(self):
        queryset1 = Content.search_objects.search(feature_types=[self.feature_type1.slug])
        queryset2 = Content.search_objects.search(feature_types=[self.feature_type2.slug])
        reading_list = SearchSlicer()
        reading_list.register_queryset(queryset1)

        def even_validator(index):
            return bool(index % 2 == 0)

        reading_list.register_queryset(queryset2, validator=even_validator)
        out = [obj for obj in reading_list]
        for obj in queryset1:
            index = out.index(obj)
            self.assertTrue(bool(index % 2 != 0))
        for obj in queryset2:
            index = out.index(obj)
            self.assertTrue(bool(index % 2 == 0))

    def test_stop_iteration_exception(self):
        queryset1 = Content.search_objects.search(feature_types=[self.feature_type1.slug])
        queryset2 = Content.search_objects.search(feature_types=[self.feature_type2.slug])
        queryset2 = queryset2.filter(es_filter.Terms(**{"id": [queryset2[0].id]}))
        reading_list = SearchSlicer()
        reading_list.register_queryset(queryset1)

        def even_validator(index):
            return bool(index % 2 == 0)

        reading_list.register_queryset(queryset2, validator=even_validator)
        out = [obj for obj in reading_list]
        for obj in queryset1:
            self.assertIn(obj, out)
        for obj in queryset2:
            index = out.index(obj)
            self.assertTrue(bool(index % 2 == 0))


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
        self.assertEqual(
            sorted(search_party.query),
            sorted({
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
            })
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
        search = search_party.search()
        self.assertEqual(search.count(), 2)
        expected_content = list(sc1.get_content()) + list(sc2.get_content())
        for obj in search:
            self.assertIn(obj, expected_content)

        sc2.query["included_ids"] = [self.content_list[1].id]
        sc2.save()
        search_party = SearchParty(self.special_coverages)
        search = search_party.search()
        self.assertEqual(search.count(), 3)
        expected_content.append(self.content_list[1])
        for obj in search:
            self.assertIn(obj, expected_content)

        sc2.query["pinned_ids"] = [self.content_list[3].id]
        sc2.save()
        search_party = SearchParty(self.special_coverages)
        search = search_party.search()
        self.assertEqual(search.count(), 4)
        expected_content.append(self.content_list[3])
        for obj in search:
            self.assertIn(obj, expected_content)

        sc2.query["excluded_ids"] = [sc1.get_content()[0].id]
        sc2.save()
        search_party = SearchParty(self.special_coverages)
        search = search_party.search()
        self.assertEqual(search.count(), 3)
        expected_content.pop(expected_content.index(sc1.get_content()[0]))
        for obj in search:
            self.assertIn(obj, expected_content)

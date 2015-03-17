import copy
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from elastimorphic.tests.base import BaseIndexableTestCase
from rest_framework.test import APIClient

from bulbs.content.models import Content, FeatureType, Tag
from bulbs.content.custom_search import custom_search_model

from tests.testcontent.models import TestContentObj, TestContentObjTwo
from tests.utils import BaseAPITestCase, make_content


class BaseCustomSearchFilterTests(BaseIndexableTestCase):
    """Base test case that sets up some data."""
    def setUp(self):
        super(BaseCustomSearchFilterTests, self).setUp()
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

        # NOTE: we updated some field names after I initially typed this up.
        # NOTE: These functions munge the existing data into the new form.
        def makeGroups(groups):
            result = []
            for group in groups:
                if isinstance(group, dict):
                    this_group = group
                else:
                    this_group = dict(conditions=[])
                    for condition in group:
                        this_group["conditions"].append(makeCondition(*condition))
                result.append(this_group)
            return result

        def makeCondition(field, type, values):
            return dict(
                field=field, type=type,
                values=[dict(label=v, value=v) for v in values]
            )

        s_biden = dict(
            label="All Biden, Baby",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "all", [self.tags[1].slug]),
                    ],
                ])
            )
        )
        s_obama = dict(
            label="All Obama, Baby",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "all", [self.tags[0].slug]),
                    ],
                ])
            )
        )
        # logical and
        s_b_and_b = dict(
            label="Obama and Biden, together!",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "all", [
                            self.tags[0].slug,
                            self.tags[1].slug
                        ]),
                    ],
                ])
            )
        )
        # logical or
        s_b_or_b = dict(
            label="Obama or Biden, whatever!",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "any", [
                            self.tags[0].slug,
                            self.tags[1].slug
                        ]),
                    ],
                ])
            )
        )
        # excluding some tags
        s_lite_obama = dict(
            label="Obama but not political stuff",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "all", [
                            self.tags[0].slug,  # obama
                        ]),
                        ("tag", "none", [
                            self.tags[4].slug,  # politics
                        ]),
                    ],
                ])
            )
        )
        # multiple, disjoint groups
        s_funny_and_slideshows = dict(
            label="Anything funny and also slideshows!",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "any", [
                            self.tags[3].slug  # funny tags
                        ]),
                    ],
                    [
                        ("feature-type", "any", [
                            self.feature_types[1].slug  # slideshow
                        ]),
                    ],
                ])
            )
        )
        # this tag is on everything
        s_wow = dict(
            label="Wow!",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "all", [
                            self.tags[2].slug  # funny tags
                        ]),
                    ],
                ])
            )
        )
        # filter by content type
        s_doctype = dict(
            label="Doctype",
            query=dict(
                groups=makeGroups([
                    [
                        ("content-type", "all", [
                            TestContentObjTwo.get_mapping_type_name()
                        ])
                    ]
                ])
            )
        )
        # include some ids
        s_one_article = dict(
            label="Just this article",
            query=dict(
                groups=[],
                included_ids=[self.content_list[0].id]
            )
        )
        s_two_articles = dict(
            label="Just two articles",
            query=dict(
                groups=[],
                included_ids=[
                    self.content_list[0].id,
                    self.content_list[3].id
                ]
            )
        )
        # exclude ids
        s_all_but_one_article = dict(
            label="All but one article",
            query=dict(
                groups=[],
                excluded_ids=[
                    self.content_list[0].id
                ]
            )
        )
        # last day of articles
        s_last_day = dict(
            label="Last day",
            query=dict(
                groups=[dict(
                    conditions=[],
                    time="1 day"
                )],
            )
        )
        # pinned
        s_pinned = dict(
            label="Pinned something",
            query=dict(
                pinned_ids=[
                    content_list[-1].id  # last in time
                ]
            )
        )
        # pinned 2 
        s_pinned_2 = dict(
            label="Pinned 2 things",
            query=dict(
                pinned_ids=[
                    content_list[-1].id,  # last in time
                    content_list[-2].id  # penultimate
                ]
            )
        )
        # pinned 2 with groups
        s_pinned_2_groups = dict(
            label="Pinned 2 things with other filters",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "any", [
                            self.tags[0].slug,
                            self.tags[1].slug,
                            self.tags[2].slug,
                            self.tags[3].slug,
                            self.tags[4].slug
                        ]),
                    ]
                ]),
                pinned_ids=[
                    content_list[-1].id,  # last in time
                    content_list[-2].id  # penultimate
                ]
            )
        )
        # text query
        s_text_query = dict(
            label="Text query",
            query=dict(
                query="again"
            )
        )
        # text query with pinned ids
        s_text_query_pinned = dict(
            label="Text query",
            query=dict(
                groups=makeGroups([
                    [
                        ("tag", "any", [self.tags[2].slug]),
                    ]
                ]),
                pinned_ids=[self.content_list[4].id],
                query="Flawless"
            )
        )
        # saved search and the expected result count
        self.search_expectations = (
            (s_biden, 2),
            (s_obama, 4),
            (s_b_and_b, 1),
            (s_b_or_b, 5),
            (s_lite_obama, 2),
            (s_funny_and_slideshows, 2),
            (s_wow, len(self.content_list)),
            (s_one_article, 1),
            (s_two_articles, 2),
            (s_all_but_one_article, len(self.content_list) - 1),
            (s_last_day, 3),
            (s_pinned, len(self.content_list)),
            (s_pinned_2, len(self.content_list)),
            (s_pinned_2_groups, len(self.content_list)),
            (s_doctype, TestContentObjTwo.objects.count()),
            (s_text_query, 2),
            (s_text_query_pinned, 2),
        )
        self.preview_expectations = (
            (s_biden, 2),
            (s_obama, 4),
            (s_b_and_b, 1),
            (s_b_or_b, 5),
            (s_lite_obama, 2),
            (s_funny_and_slideshows, 2),
            (s_wow, len(self.content_list)),
            (s_one_article, 1),
            (s_two_articles, 2),
            (s_all_but_one_article, len(self.content_list)), # excluded
            (s_last_day, 3),
            (s_doctype, TestContentObjTwo.objects.count()),
            (s_text_query, 2),
            (s_text_query_pinned, 2),
        )
        self.group_preview_expectations = (
            (s_biden, 2),
            (s_obama, 4),
            (s_b_and_b, 1),
            (s_wow, len(self.content_list)),
            (s_one_article, 1),
            (s_two_articles, 2),
            (s_all_but_one_article, len(self.content_list)), # excluded
        )
        # is not published and not is_preview
        self.unpublished_expectations = (
            (s_biden, 2),
            (s_obama, 4),
            (s_b_and_b, 1),
            (s_b_or_b, 5),
            (s_lite_obama, 2),
            (s_funny_and_slideshows, 2),
            (s_wow, len(self.content_list)),
            (s_one_article, 1),
            (s_two_articles, 2),
            (s_all_but_one_article, len(self.content_list) - 1),
            (s_last_day, 3),
            (s_pinned, len(self.content_list)),
            (s_pinned_2, len(self.content_list)),
            (s_pinned_2_groups, len(self.content_list)),
            (s_text_query, 2),
            (s_text_query_pinned, 2),
        )
        # is published and not is_preview
        self.published_expectations = (
            (s_biden, 2),
            (s_obama, 3),
            (s_b_and_b, 1),
            (s_b_or_b, 5 - 1),
            (s_lite_obama, 2),
            (s_funny_and_slideshows, 2),
            (s_wow, len(self.content_list) - 1),
            (s_one_article, 1 - 1),
            (s_two_articles, 2 - 1),
            (s_all_but_one_article, len(self.content_list) - 1),
            (s_last_day, 2),
            (s_pinned, len(self.content_list) - 1),
            (s_pinned_2, len(self.content_list) - 1),
            (s_pinned_2_groups, len(self.content_list) - 1),
            (s_text_query, 1),
            (s_text_query_pinned, 2),
        )
        # (search filter, (list, of, ids, in, order)),
        self.ordered_expectations = (
            (s_all_but_one_article, (2, 3, 4)),
            (s_text_query_pinned, (content_list[4].id, content_list[2].id)),
        )
        self.pinned_expectations = (
            (s_pinned, (
                content_list[-1].id,
                content_list[0].id, content_list[1].id,
            )),
            (s_pinned_2, (
                content_list[-2].id, content_list[-1].id,
                content_list[0].id, content_list[1].id,
            )),
            (s_pinned_2_groups, (
                content_list[-2].id, content_list[-1].id,
                content_list[0].id, content_list[1].id,
            )),
        )


class CustomSearchFilterTests(BaseCustomSearchFilterTests):
    """Test the F() generating functions."""
    field_map = {
        "feature-type": "feature_type.slug",
        "tag": "tags.slug",
        "content-type": "_type"
    }

    def test_counts_correct(self):
        for s, count in self.search_expectations:
            self.check_filtered_count(s["query"], count)

    def check_filtered_count(self, query, expected_count):
        qs = custom_search_model(Content, query, field_map=self.field_map)
        self.assertEqual(qs.count(), expected_count)

    def test_preview_counts_correct(self):
        for s, count in self.preview_expectations:
            self.check_preview_filter_count(s["query"], count)

    def check_preview_filter_count(self, query, expected_count):
        qs = custom_search_model(Content, query, preview=True, field_map=self.field_map)
        self.assertEqual(qs.count(), expected_count)

    def test_ordering(self):
        for s, ids in self.ordered_expectations:
            self.check_ordering(s["query"], ids)

    def test_pinned(self):
        for s, ids in self.pinned_expectations:
            self.check_ordering(s["query"], ids)
        
    def check_ordering(self, query, ids):
        qs = custom_search_model(Content, query, field_map=self.field_map)
        self.assertSequenceEqual([c.id for c in qs[:len(ids)]], ids)


class BaseCustomSearchApiTests(BaseAPITestCase, BaseCustomSearchFilterTests):
    """Makes sure we're getting the same data through the API."""
    def setUp(self):
        super(BaseCustomSearchApiTests, self).setUp()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.admin)


class ResultsApiTests(BaseCustomSearchApiTests):
    """Test for the list results API view."""
    def test_api_counts_correct(self):
        for s, count in self.search_expectations:
            self.check_api_counts(s["query"], count)

    def check_api_counts(self, query, expected_count):
        endpoint_url = reverse("custom-search-content-list")
        payload = copy.deepcopy(query)
        payload["preview"] = False
        r = self.api_client.post(endpoint_url, payload, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], expected_count)

    def test_api_preview_counts_correct(self):
        for s, expected_count in self.preview_expectations:
            self.check_api_preview_counts(s["query"], expected_count)

    def check_api_preview_counts(self, query, expected_count):
        endpoint_url = reverse("custom-search-content-list")
        r = self.api_client.post(endpoint_url, query, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], expected_count)


class CountsApiTests(BaseCustomSearchApiTests):
    """Tests for the /counts API view."""
    def test_api_counts_correct(self):
        for s, count in self.search_expectations:
            self.check_api_counts(s["query"], count)

    def check_api_counts(self, query, expected_count):
        endpoint_url = reverse("custom-search-content-count")
        payload = copy.deepcopy(query)
        payload["preview"] = False
        r = self.api_client.post(endpoint_url, payload, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], expected_count)

    def test_api_preview_counts_correct(self):
        for s, count in self.preview_expectations:
            self.check_api_preview_counts(s["query"], count)

    def check_api_preview_counts(self, query, expected_count):
        endpoint_url = reverse("custom-search-content-count")
        r = self.api_client.post(endpoint_url, query, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], expected_count)

    def test_api_group_preview_counts_correct(self):
        for s, count in self.group_preview_expectations:
            self.check_api_group_preview_counts(s["query"], count)

    def check_api_group_preview_counts(self, query, expected_count):
        groups = query.get("groups")
        if not groups:
            return
        group = groups[0]
        endpoint_url = reverse("custom-search-content-group-count")
        r = self.api_client.post(endpoint_url, group, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], expected_count)


class ContentCustomSearchListViewTestCase(BaseCustomSearchFilterTests):
    """Test the ListView."""
    def test_published_list_view(self):
        url = reverse("tests.testcontent.views.test_published_content_custom_search_list")
        for s, expected_count in self.published_expectations:
            r = self.client.post(url, json.dumps(dict(query=s["query"])), content_type="application/json")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.context_data["paginator"].count, expected_count)
            
    def test_unpublished_list_view(self):
        url = reverse("tests.testcontent.views.test_unpublished_content_custom_search_list")
        for s, expected_count in self.search_expectations:
            r = self.client.post(url, json.dumps(dict(query=s["query"])), content_type="application/json")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.context_data["paginator"].count, expected_count)

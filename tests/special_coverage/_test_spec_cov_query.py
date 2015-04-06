
from datetime import timedelta

from django.utils import timezone

from bulbs.content.models import Content, FeatureType, Tag
from bulbs.special_coverage.models import SpecialCoverage

from example.testcontent.models import TestContentObjTwo
from bulbs.utils.test import BaseIndexableTestCase, make_content


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
                            TestContentObjTwo.mapping.doc_type
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
        self.published_not_pinned_expectations = (
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


class SpecialCoverageQueryTests(BaseCustomSearchFilterTests):

    def setUp(self):
        super(SpecialCoverageQueryTests, self).setUp()

    def test_get_content(self):
        """tests the search results are instances of Content"""

        query = self.search_expectations[1][0]
        sc = SpecialCoverage.objects.create(
            name="All Obama, Baby",
            description="All Obama, Baby",
            query=query
        )
        res = sc.get_content()
        for content in res:
            self.assertIsInstance(content, Content)

    def test_has_pinned_content(self):
        """tests that the .has_pinned_content accurately returns True or False"""

        query = self.search_expectations[0][0]
        sc = SpecialCoverage.objects.create(
            name="All Biden, Baby",
            description="All Biden, Baby",
            query=query
        )

        self.assertTrue(hasattr(sc, "has_pinned_content"))
        self.assertFalse(sc.has_pinned_content)

        query = self.search_expectations[-1][0]
        sc = SpecialCoverage.objects.create(
            name="Text query",
            description="Text query",
            query=query
        )

        self.assertTrue(hasattr(sc, "has_pinned_content"))
        self.assertTrue(sc.has_pinned_content)

    def test_contents(self):
        """tests that the .contents accurately returns Content objects"""

        query = self.search_expectations[2][0]
        sc = SpecialCoverage.objects.create(
            name="Obama and Biden, together",
            description="Obama and Biden, together",
            query=query
        )

        self.assertTrue(hasattr(sc, "contents"))
        for content in sc.contents:
            self.assertIsInstance(content, Content)

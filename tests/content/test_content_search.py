from __future__ import absolute_import

import itertools
import datetime
import time
import pytest


from django.utils import timezone
from django.test.client import Client
from django.template.defaultfilters import slugify

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.content.models import Content, Tag, FeatureType
from example.testcontent.models import TestContentObj, TestContentObjTwo
from bulbs.utils.test import make_content


class PolyContentTestCase(BaseIndexableTestCase):
    def setUp(self):
        super(PolyContentTestCase, self).setUp()
        """
        Normally, the "Content" class picks up available doctypes from installed apps, but
        in this case, our test models don't exist in a real app, so we'll hack them on.
        """

        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        words = ['spam', 'driver', 'dump truck', 'restaurant']
        self.num_subclasses = 2
        self.combos = list(itertools.combinations(words, 2))
        self.all_tags = []
        ft_one = FeatureType.objects.create(name="Obj one", slug="obj-one")
        ft_two = FeatureType.objects.create(name="Obj two", slug="obj-two")

        for i, combo in enumerate(self.combos):
            tags = []
            for atom in combo:
                tag, created = Tag.objects.get_or_create(name=atom, slug=slugify(atom))
                tags.append(tag)
                self.all_tags.append(tag)

            obj = make_content(TestContentObj, published=one_hour_ago, feature_type=ft_one)
            obj.tags.add(*tags)
            obj.index()

            obj2 = make_content(TestContentObjTwo, published=two_days_ago, feature_type=ft_two)
            obj2.tags.add(*tags)
            obj2.index()

        obj = TestContentObj.objects.create(
            title="Unpublished draft",
            description="Just to throw a wrench",
            foo="bar",
            feature_type=ft_one
        )
        Content.search_objects.refresh()

    def test_filter_search_content(self):

        self.assertEqual(Content.objects.count(), 13)  # The 12, plus the unpublished one

        q = Content.search_objects.search()
        self.assertEqual(q.count(), 12)

        q = Content.search_objects.search(query="spam")
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(tags=["spam"])
        self.assertEqual(len(q), 6)
        self.assertEqual(q.count(), 6)
        for content in q:
            slugs = [tag.slug for tag in content.tags.all()]
            self.assertTrue("spam" in slugs)

        q = Content.search_objects.search(feature_types=["obj-one"])
        self.assertEqual(q.count(), 6)
        for content in q:
            self.assertEqual("Obj one", content.feature_type.name)

        q = Content.search_objects.search(types=["testcontent_testcontentobj"])
        self.assertEqual(q.count(), 6)

        # date before
        before = timezone.now()
        q = Content.search_objects.search(before=before)
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(before=before.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 12)

        before = timezone.now() - datetime.timedelta(hours=4)
        q = Content.search_objects.search(before=before)
        self.assertEqual(q.count(), 6)
        q = Content.search_objects.search(before=before.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 6)

        # date after
        after = timezone.now() - datetime.timedelta(hours=4)
        q = Content.search_objects.search(after=after)
        self.assertEqual(q.count(), 6)
        q = Content.search_objects.search(after=after.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 6)

        after = timezone.now() - datetime.timedelta(days=40)
        q = Content.search_objects.search(after=after)
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(after=after.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 12)

        # assorted date types - datetime.date, datetime.datetime.strftime, iso string
        after = timezone.now() - datetime.timedelta(days=40)
        date_after = datetime.date(after.year, after.month, after.day)
        q = Content.search_objects.search(after=date_after)
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(after=after.strftime("%Y-%m-%d"))
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(after="1970-01-01T01:01:01.123456+03:00")
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(after="1970-1-1T01:01:01.123456+03:00")
        self.assertEqual(q.count(), 12)

        # date range tests
        before = timezone.now() - datetime.timedelta(seconds=1)
        after = timezone.now() - datetime.timedelta(seconds=20)
        q = Content.search_objects.search(before=before, after=after)
        self.assertEqual(q.count(), 0)
        q = Content.search_objects.search(
            before=before.strftime("%Y-%m-%d %H:%M:%S"), after=after.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 0)

        before = timezone.now() - datetime.timedelta(hours=1)
        after = timezone.now() - datetime.timedelta(days=7)
        q = Content.search_objects.search(before=before, after=after)
        self.assertEqual(q.count(), 12)
        q = Content.search_objects.search(
            before=before.strftime("%Y-%m-%d %H:%M:%S"), after=after.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 12)

        before = timezone.now() - datetime.timedelta(days=7)
        after = timezone.now() - datetime.timedelta(days=14)
        q = Content.search_objects.search(before=before, after=after)
        self.assertEqual(q.count(), 0)
        q = Content.search_objects.search(
            before=before.strftime("%Y-%m-%d %H:%M:%S"), after=after.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(q.count(), 0)
        # /date range tests

        q = Content.search_objects.search(types=["testcontent_testcontentobjtwo"])
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(types=[
            "testcontent_testcontentobjtwo", "testcontent_testcontentobj"])
        self.assertEqual(q.count(), 12)

    def test_status_filter(self):
        q = Content.search_objects.search(status="final")
        self.assertEqual(q.count(), 12)

        q = Content.search_objects.search(status="draft")
        self.assertEqual(q.count(), 1)

    def test_negative_filters(self):
        q = Content.search_objects.search(tags=["-spam"])
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(feature_types=["-obj-one"])
        self.assertEqual(q.count(), 6)
        for content in q:
            self.assertNotEqual("Obj one", content.feature_type.name)

    def test_content_subclasses(self):
        # We created one of each subclass per combination so the following should be true:
        self.assertEqual(Content.objects.count(), (len(self.combos) * self.num_subclasses) + 1)
        self.assertEqual(TestContentObj.objects.count(), len(self.combos) + 1)
        self.assertEqual(TestContentObjTwo.objects.count(), len(self.combos))

    def test_content_list_view(self):
        client = Client()
        response = client.get('/content_list_one.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['object_list']), len(self.combos) * self.num_subclasses)

    def test_add_remove_tags(self):
        content = make_content()
        original_tag_count = len(content.tags.all())
        new_tag = Tag.objects.create(name='crankdat')
        content.tags.add(new_tag)
        self.assertEqual(len(content.tags.all()), original_tag_count + 1)
        self.assertEqual(len(content.tags.all()), len(content.to_dict()["tags"]))

    def test_search_exact_name_tags(self):
        Tag.objects.create(name="Beeftank")
        Tag.search_objects.refresh()
        results = Tag.search_objects.search().query({"match": {"name": "Beeftank"}})
        assert results.count() == 1
        assert isinstance(results[0], Tag)

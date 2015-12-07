from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import timezone

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase, make_content

from example.testcontent.models import TestContentObj


class RSSTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def test_rss_feed(self):
        # Let's bust out some content
        make_content(TestContentObj, published=timezone.now() - timedelta(hours=2), _quantity=35)
        TestContentObj.search_objects.refresh()

        rss_endpoint = reverse("rss-feed")

        client = Client()
        response = client.get(rss_endpoint)
        self.assertEqual(response.status_code, 200)

        first_item = response.context["page_obj"].object_list[0]
        self.assertTrue(hasattr(first_item, "feed_url"))

    def test_rss_pagination(self):
        endpoint = reverse("rss-feed")
        for i in range(40):
            TestContentObj.objects.create(
                title='Content #{}'.format(i),
                published=timezone.now() - timezone.timedelta(days=i)
            )
        TestContentObj.search_objects.refresh()

        client = Client()
        resp = client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        page1_content_list = resp.context_data.get('content_list')
        self.assertEqual(len(page1_content_list), 20)

        resp = client.get(endpoint, {'page': 2})
        self.assertEqual(resp.status_code, 200)
        page2_content_list = resp.context_data.get('content_list')
        self.assertEqual(len(page2_content_list), 20)

        for content in page1_content_list:
            self.assertNotIn(content, page2_content_list)

    def test_special_coverage_rss_feed(self):
        # make content
        c1 = TestContentObj.objects.create(title="Content1", published=timezone.now())
        c2 = TestContentObj.objects.create(title="Content2", published=timezone.now())
        TestContentObj.objects.create(title="Content3", published=timezone.now())
        TestContentObj.search_objects.refresh()

        # make Special Coverage & add c1 & c2 to it
        sc = SpecialCoverage.objects.create(
            name="Coverage",
            description="Test coverage",
            query={
                'excluded_ids': [],
                'groups': [],
                'included_ids': [c1.pk, c2.pk],
                'pinned_ids': []
            }
        )

        # test slug w/ sc-rss-feed
        sc_rss = reverse("sc-rss-feed")
        client = Client()
        response = client.get("{0}?special_coverage_slug={1}".format(sc_rss, sc.slug))

        self.assertEqual(response.status_code, 200)

        # verify stuff is in sc-rss-feed response
        self.assertTrue("Content1" in response.content.decode('utf-8'))
        self.assertTrue("Content2" in response.content.decode('utf-8'))
        self.assertTrue("Content3" not in response.content.decode('utf-8'))

        # test id w/ sc-rss-feed
        response = client.get("{0}?special_coverage_id={1}".format(sc_rss, sc.id))
        self.assertEqual(response.status_code, 200)

        # verify stuff is in sc-rss-feed response
        self.assertTrue("Content1" in response.content.decode('utf-8'))
        self.assertTrue("Content2" in response.content.decode('utf-8'))
        self.assertTrue("Content3" not in response.content.decode('utf-8'))

        # test w/o id or slug
        response = client.get("{0}".format(sc_rss))
        self.assertEqual(response.status_code, 200)

        # verify nothing is returned
        object_list = response.context["page_obj"].object_list
        self.assertEqual(len(object_list), 0)

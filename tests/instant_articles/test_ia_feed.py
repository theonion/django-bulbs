from bulbs.content.models import FeatureType
from bulbs.utils.test import BaseIndexableTestCase

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase
from django.test.client import Client

from example.testcontent.models import TestContentObj

class InstantArticleTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(InstantArticleTestCase, self).setUp()
        self.news_in_brief = FeatureType.objects.create(name='News In Brief')

    def test_pagination(self):
        for i in range(100):
            TestContentObj.objects.create(
                title='TestContentObj #{}'.format(i),
                feature_type=self.news_in_brief,
                published=timezone.now() - timezone.timedelta(days=i),
                instant_article=True
            )
        TestContentObj.search_objects.refresh()

        endpoint = reverse('instant_articles')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)

        content_list = resp.context_data['content_list']
        self.assertEqual(len(content_list), 100)

    def test_invalid_feature_types(self):
        news = FeatureType.objects.create(name='News')
        s_news_in_brief = FeatureType.objects.create(name='Sports News In Brief')
        article = FeatureType.objects.create(name='Article')
        news_in_photos = FeatureType.objects.create(name='News In Photos')

        for feature_type in [news, s_news_in_brief, article]:
            TestContentObj.objects.create(
                title="TestContentObj - {}".format(feature_type.name),
                feature_type=feature_type,
                published = timezone.now() - timezone.timedelta(days=2),
                instant_article=True
            )
        nip = TestContentObj.objects.create(
            title="TestContentObj - {}".format(feature_type.name),
            feature_type=news_in_photos,
            published = timezone.now() - timezone.timedelta(days=2),
            instant_article=True
        )

        TestContentObj.search_objects.refresh()
        endpoint = reverse('instant_articles')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        content_list = resp.context_data['content_list']
        self.assertEqual(len(content_list), 3)
        for item in content_list:
            self.assertNotIn(item.id, [nip.id])

    def test_instant_article_filter(self):
        published_time = timezone.now() - timezone.timedelta(days=2)
        instant_article = TestContentObj.objects.create(
            title="NIB Instant Article",
            feature_type=self.news_in_brief,
            published=published_time,
            instant_article=True
        )
        non_instant_article = TestContentObj.objects.create(
            title="NIB Non-Instant Article",
            feature_type=self.news_in_brief,
            published=published_time,
            instant_article=False
        )
        TestContentObj.search_objects.refresh()
        endpoint = reverse('instant_articles')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        content_list = resp.context_data['content_list']
        self.assertEqual(len(content_list), 1)
        self.assertEqual(content_list[0].id, instant_article.id)

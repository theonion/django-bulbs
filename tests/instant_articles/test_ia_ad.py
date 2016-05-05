from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class InstantArticleAdViewTests(BaseIndexableTestCase):
    def setUp(self):
        super(InstantArticleAdViewTests, self).setUp()
        self.client = Client()
        self.feature_type = FeatureType.objects.create(name="AdBoys", instant_article=True)
        self.content = make_content(TestContentObj, feature_type=self.feature_type)
        self.url = reverse("instant_article_ad", kwargs={"pk": self.content.pk})

    def test_ad_unit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # TODO: bubble up ad formatting.
        # self.assertInHTML(
        #     '<div class="dfp dfp-slot-instant-article-inread" data-ad-unit="instant-article-inread" >',
        #     str(response.content)
        # )

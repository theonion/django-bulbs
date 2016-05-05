from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class AnalyticsViewTests(BaseIndexableTestCase):

    def setUp(self):
        super(AnalyticsViewTests, self).setUp()
        self.feature_type = FeatureType.objects.create(
            name="Ey go that way bruh", instant_article=True
        )
        self.content = make_content(TestContentObj, feature_type=self.feature_type)

    def test_analytics(self):
        self.client = Client()
        url = reverse("instant_article_analytics", kwargs={"pk": self.content.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Instant Articles", response.context_data.get("platform"))

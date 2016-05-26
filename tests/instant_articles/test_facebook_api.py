import requests_mock

from django.utils import timezone
from django.test.utils import override_settings

from bulbs.content.models import FeatureType
from bulbs.utils.test import BaseIndexableTestCase
from bulbs.utils.test.mock_vault import mock_vault

from example.testcontent.models import TestContentObjThree


class FacebookAPITestCase(BaseIndexableTestCase):

    def setUp(self):
        super(FacebookAPITestCase, self).setUp()
        self.ft = FeatureType.objects.create(name="NIP", instant_article=True)

    @mock_vault({'facebook/onion/token': {'value': '123abc'}})
    @override_settings(FACEBOOK_PAGE_ID='123456')
    def test_publish_to_facebook_on_save(self):
        with requests_mock.mock() as m:
            content = TestContentObjThree.objects.create(
                body="<p>This is the body</p>",
                feature_type=self.ft)
            content.published = timezone.now()
            content.save()

    def test_log_errors(self):
        pass
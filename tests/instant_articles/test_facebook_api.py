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

    # @mock_vault({'facebook/onion/token': {'value': '123abc'}})
    @override_settings(
        FACEBOOK_PAGE_ID='123456',
        FACEBOOK_API_BASE_URL='https://graph.facebook.com/v2.6',
        WWW_URL='www.theonion.com',
        BETTY_FIXED_URL='http://i.onionstatic.com/onion'
    )
    def test_publish(self):
        with requests_mock.mock() as mocker:
            # post to instant article endpoit
            mocker.post(
                "https://graph.facebook.com/v2.6/123456/instant_articles",
                status_code=200,
                json={
                    "id": 456
                }
            )

            # get status of instant article
            mocker.get(
                "https://graph.facebook.com/v2.6/456?access_token=123abc",
                status_code=200,
                json={
                    "id": 9876,
                    "success": True
                }
            )

            content = TestContentObjThree.objects.create(
                body="<p>This is the body</p>",
                feature_type=self.ft)
            content.published = timezone.now()
            content.save()

            self.assertEqual(content.instant_article_id, 9876)

    def test_publish_status_error(self):
        pass
        # save and publish article w/ status of error
        # check that logger was called

    def test_unpublish(self):
        pass
        # save & publish article
        # unpublish & check delete was called

    def test_delete(self):
        pass
        # save & publish article
        # call delete on object & check delete was called
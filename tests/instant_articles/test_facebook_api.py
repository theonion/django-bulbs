import requests_mock

from django.conf import settings
from django.utils import timezone
from django.test.utils import override_settings

from bulbs.content.models import FeatureType, Content
from bulbs.utils.test import BaseIndexableTestCase
from bulbs.utils.test.mock_vault import mock_vault

from example.testcontent.models import TestContentObjThree


class FacebookAPITestCase(BaseIndexableTestCase):

    def setUp(self):
        super(FacebookAPITestCase, self).setUp()
        self.ft = FeatureType.objects.create(name="NIP", instant_article=True)

    @override_settings(
        FACEBOOK_POST_TO_IA=True,
        BETTY_FIXED_URL='http://i.onionstatic.com/onion')
    @mock_vault({'facebook/onion_token': {'authtoken': 'TOKEN'}})
    def test_publish(self):
        with requests_mock.mock() as mocker:
            # post to instant article endpoit
            mocker.post(
                "https://graph.facebook.com/v2.6/123456/instant_articles",
                status_code=200,
                json={
                    "id": 456
                })
            # get status of instant article
            mocker.get(
                "https://graph.facebook.com/v2.6/456?access_token=TOKEN",
                status_code=200,
                json={
                    "id": 9876,
                    "status": "SUCCESS"
                })

            # create content
            content = TestContentObjThree.objects.create(
                body="<p>This is the body</p>",
                feature_type=self.ft)

            # get article ID
            mocker.get(
                "https://graph.facebook.com/v2.6?id=http://www.theonion.com{0}&amp;fields=instant_article&amp;access_token=TOKEN".format(
                    content.get_absolute_url()),
                status_code=200,
                json={"instant_article": {
                        "id": "420"
                    },
                    "id": "http://www.theonion.com/article/blaze-it-420"
                }
            )

            content.published = timezone.now()
            content.save()

            Content.search_objects.refresh()
            c = Content.objects.get(id=content.id)

            # check that the ia_id is set & call count is correct
            self.assertEqual(c.instant_article_id, 420)
            self.assertEqual(mocker.call_count, 3)

    @override_settings(
        FACEBOOK_POST_TO_IA=True,
        BETTY_FIXED_URL='http://i.onionstatic.com/onion')
    @mock_vault({'facebook/onion_token': {'authtoken': 'TOKEN'}})
    def test_unpublish(self):
        with requests_mock.mock() as mocker:
            mocker.post(
                "https://graph.facebook.com/v2.6/123456/instant_articles",
                status_code=201,
                json={
                    "id": 456
                })
            mocker.get(
                "https://graph.facebook.com/v2.6/456?access_token=TOKEN",
                status_code=200,
                json={
                    "id": 9876,
                    "status": "SUCCESS"
                })
            mocker.delete(
                "https://graph.facebook.com/v2.6/420?access_token=TOKEN",
                status_code=204,
                json={
                    "success": True
                })

            content = TestContentObjThree.objects.create(
                body="<p>This is the body</p>",
                feature_type=self.ft)

            mocker.get(
                "https://graph.facebook.com/v2.6?id=http://www.theonion.com{0}&amp;fields=instant_article&amp;access_token=TOKEN".format(
                    content.get_absolute_url()),
                status_code=200,
                json={"instant_article": {
                        "id": "420"
                    },
                    "id": "http://www.theonion.com/article/blaze-it-420"
                }
            )

            content.published = timezone.now()
            content.save()

            Content.search_objects.refresh()
            c = Content.objects.get(id=content.id)

            self.assertEqual(c.instant_article_id, 420)
            self.assertEqual(mocker.call_count, 3)

            # unpublish article and check that delete is called
            c.published = timezone.now() + timezone.timedelta(days=1)
            c.save()

            self.assertEqual(mocker.call_count, 4)

    @override_settings(
        FACEBOOK_POST_TO_IA=True,
        BETTY_FIXED_URL='http://i.onionstatic.com/onion')
    @mock_vault({'facebook/onion_token': {'authtoken': 'TOKEN'}})
    def test_delete(self):
        with requests_mock.mock() as mocker:
            mocker.post(
                "https://graph.facebook.com/v2.6/123456/instant_articles",
                status_code=201,
                json={
                    "id": 456
                })
            mocker.get(
                "https://graph.facebook.com/v2.6/456?access_token=TOKEN",
                status_code=200,
                json={
                    "id": 9876,
                    "status": "SUCCESS"
                })
            mocker.delete(
                "https://graph.facebook.com/v2.6/420?access_token=TOKEN",
                status_code=204,
                json={
                    "success": True
                })

            content = TestContentObjThree.objects.create(
                body="<p>This is the body</p>",
                feature_type=self.ft)

            mocker.get(
                "https://graph.facebook.com/v2.6?id=http://www.theonion.com{0}&amp;fields=instant_article&amp;access_token=TOKEN".format(
                    content.get_absolute_url()),
                status_code=200,
                json={"instant_article": {
                        "id": "420"
                    },
                    "id": "http://www.theonion.com/article/blaze-it-420"
                }
            )

            content.published = timezone.now()
            content.save()

            self.assertEqual(mocker.call_count, 3)

            content.delete()

            self.assertEqual(mocker.call_count, 4)

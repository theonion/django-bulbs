import json

from django.core.urlresolvers import reverse

from bulbs.notifications.models import Notification
from bulbs.utils.test import BaseAPITestCase


DEFAULT_NOTIFICATION_DATA = {
    'internal_title': 'rio: part 1.',
    'headline': 'You can do it nicky!',
    'body': 'Little Nicky is the greatest movie of all time.',
    'image': {'id': 1},
    'clickthrough_url': 'https://www.clickhole.com'
}


def create_notifications(quantity=60):
    for i in range(quantity):
        if i % 2:
            is_published = True
        else:
            is_published = False
        Notification.objects.create(is_published=is_published, **DEFAULT_NOTIFICATION_DATA)


class NotificationAPITestCase(BaseAPITestCase):

    def setUp(self):
        super(NotificationAPITestCase, self).setUp()
        self.list_endpoint = reverse('notification-list')
        self.notification_data = DEFAULT_NOTIFICATION_DATA
        create_notifications()

    def test_list_endpoint(self):
        self.assertEqual(self.list_endpoint, '/api/v1/notification/')

    def test_detail_endpoint(self):
        notification = Notification.objects.first()
        self.assertEqual(
            self.get_detail_endpoint(notification.pk),
            '/api/v1/notification/{}/'.format(notification.pk)
        )

    def test_list_view_success(self):
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 60)
        self.assertIn('page=2', resp.data['next'])
        results = resp.data.get('results')
        self.assertEqual(len(results), 20)

    def test_public_list_view_failure(self):
        resp = self.client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 403)

    def test_post_list_view_success(self):
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.notification_data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 201)
        id = resp.data.get('id')
        self.assertTrue(Notification.objects.filter(id=id).exists())

    def test_get_detail_success(self):
        notification = Notification.objects.first()
        endpoint = self.get_detail_endpoint(notification.pk)
        resp = self.api_client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['headline'], notification.headline)
        self.assertEqual(resp.data['body'], notification.body)
        self.assertEqual(resp.data['internal_title'], notification.internal_title)
        self.assertEqual(resp.data['is_published'], notification.is_published)
        self.assertEqual(resp.data['image'], str(notification.image.id))
        self.assertEqual(resp.data['clickthrough_url'], notification.clickthrough_url)
        self.assertEqual(resp.data['clickthrough_cta'], notification.clickthrough_cta)

    def test_put_detail_success(self):
        notification = Notification.objects.first()
        endpoint = self.get_detail_endpoint(notification.pk)
        data = self.notification_data
        data['internal_title'] = 'Nevermind'
        resp = self.api_client.put(
            endpoint,
            data=json.dumps(data),
            content_type='application/json'
        )
        notification = Notification.objects.get(id=notification.id)
        self.assertEqual(notification.internal_title, data['internal_title'])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['headline'], notification.headline)
        self.assertEqual(resp.data['body'], notification.body)
        self.assertEqual(resp.data['internal_title'], notification.internal_title)
        self.assertEqual(resp.data['is_published'], notification.is_published)
        self.assertEqual(resp.data['image'], str(notification.image.id))
        self.assertEqual(resp.data['clickthrough_url'], notification.clickthrough_url)
        self.assertEqual(resp.data['clickthrough_cta'], notification.clickthrough_cta)

    def get_detail_endpoint(self, pk):
        return reverse('notification-detail', kwargs={'pk': pk})


class ReadOnlyNotificationAPITestCase(BaseAPITestCase):

    def setUp(self):
        super(ReadOnlyNotificationAPITestCase, self).setUp()
        self.list_endpoint = reverse('notification-all-list')
        self.notification_data = DEFAULT_NOTIFICATION_DATA
        create_notifications()

    def test_list_endpoint(self):
        self.assertEqual(self.list_endpoint, '/api/v1/notification-all/')

    def test_public_list_success(self):
        resp = self.client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(resp['next'], 'page=2')
        self.assertEqual(resp['count'], 30)

    def test_public_post_list_failure(self):
        resp = self.client.post(
            self.list_endpoint,
            data=json.dumps(self.notification_data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 405)

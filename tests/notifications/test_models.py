from django.test import override_settings

from bulbs.notifications.models import Notification
from bulbs.utils.test import BaseIndexableTestCase


class NotificationModelTestCase(BaseIndexableTestCase):

    def test_create_success(self):
        obj = Notification.objects.create(**self.notification_data)
        self.assertIsNotNone(obj)

    def test_created_on_auto_now(self):
        obj = Notification.objects.create(**self.notification_data)
        self.assertIsNotNone(obj.created_on)

    def test_get_clickthrough_cta_fallback(self):
        obj = Notification.objects.create(**self.notification_data)
        self.assertEqual(obj.get_clickthrough_cta(), "Read More...")

    @override_settings(NOTIFICATION_CLICKTHROUGH_CTA="Cam Time...")
    def test_get_clickthrough_cta_settings(self):
        obj = Notification.objects.create(**self.notification_data)
        self.assertEqual(obj.get_clickthrough_cta(), "Cam Time...")

    def test_get_clickthrough_cta_database(self):
        obj = Notification.objects.create(
            clickthrough_cta='what are those!!!', **self.notification_data
        )
        self.assertEqual(obj.get_clickthrough_cta(), 'what are those!!!')

    @property
    def notification_data(self):
        return {
            'internal_title': 'rio: part 1.',
            'headline': 'You can do it nicky!',
            'is_published': True,
            'body': 'Little Nicky is the greatest movie of all time.',
            'image': {'id': 1},
            'clickthrough_url': 'www.clickhole.com'
        }

import datetime

from bulbs.cms_notifications.models import CmsNotification
from elastimorphic.tests.base import BaseIndexableTestCase


class TestModels(BaseIndexableTestCase):

    def test_create(self):
        """Create a CMS notification."""

        time_now = datetime.datetime.now()

        cms_notification_1 = CmsNotification.objects.create(
            title="We've Made an Update!",
            body="Some updates were made on the site. Enjoy them while they last.",
            post_date=time_now,
            notify_end_date=time_now + datetime.timedelta(days=3),
            editable=False
        )

        cms_notification_2 = CmsNotification.objects.create(
            title="Another One!",
            body="Some updates were made on the site. Enjoy them while they last.",
            post_date=time_now,
            notify_end_date=time_now + datetime.timedelta(days=3),
            editable=False
        )

        db_cms_notifications = CmsNotification.objects.all()
        self.assertEqual(db_cms_notifications.count(), 2)
        # records should come out in reverse order of when they were created (ordering = '-id')
        self.assertEqual(cms_notification_1.title, db_cms_notifications[1].title)
        self.assertEqual(cms_notification_2.title, db_cms_notifications[0].title)

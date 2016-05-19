import mock

from django.contrib.auth import get_user_model

from bulbs.contributions.tasks import run_send_byline_email
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


User = get_user_model()


class BylineTaskTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(BylineTaskTestCase, self).setUp()
        self.king = User.objects.create(first_name="King", last_name="Kush")
        self.content = make_content(TestContentObj, published=self.now, authors=[self.king])

    def test_task_calls_send_success(self):
        with mock.patch("django.core.mail.EmailMultiAlternatives.send") as mock_send:
            run_send_byline_email.delay(self.content.id, [self.king.id])
            self.assertTrue(mock_send.called)

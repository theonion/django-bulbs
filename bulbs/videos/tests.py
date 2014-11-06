import json

from django.contrib.auth import get_user_model
# from django.conf import settings
# from django.db.models.loading import get_model
from django.test import TestCase
from django.test.client import Client


class VideoAPICase(TestCase):

    def setUp(self):
        User = get_user_model()
        # User = get_model(*settings.AUTH_USER_MODEL.split("."))
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_video_create(self):

        client = Client()
        client.login(username='admin', password='secret')

        data = {
            "name": "Testing Video"
        }
        response = client.post(
            "/videos/api/video/",
            json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)  # 201 Created
        self.assertEqual(response.data.get("name"), "Testing Video")

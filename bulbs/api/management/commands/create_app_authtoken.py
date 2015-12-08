import hashlib
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token


User = get_user_model()


class Command(BaseCommand):

    help = "Creates a new user & app token for a client request."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            dest='username',
            help='The username for the given application.',
            required=True,
            type=str
        )

    def generate_random_password(self, length=13):
        random_data = os.urandom(128)
        return hashlib.md5(random_data).hexdigest()[:16]

    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        user, created = User.objects.get_or_create(username=username, defaults={
            'password': self.generate_random_password(),
            'is_staff': True
        })
        token = Token.objects.create(user=user)
        self.stdout.write(token.key)

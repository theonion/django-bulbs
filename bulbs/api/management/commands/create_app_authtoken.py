import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token


User = get_user_model()


class Command(BaseCommand):

    help = "Creates a new user & app token for a client request."

    def add_arguments(self, parser):
        parser.add_argument(
            '-username',
            dest='username',
            help='The username for the given application.',
            required=True,
            type=str
        )

    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        qs = User.objects.filter(username=username)
        if not qs.exists():
            user = User.objects.create(
                username=username,
                is_staff=True,
                password=random.getrandbits(128)
            )
        else:
            user = qs.first()

        token = Token.objects.create(user=user)
        self.stdout.write(token.key)

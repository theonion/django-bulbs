from django.conf import settings
from django.core.signals import post_save
from django.dispatch import receiver

from .models import FreelanceProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_freelance_profile(sender, instance, **kwargs):
    FreelanceProfile.objects.get_or_create(contributor=instance)

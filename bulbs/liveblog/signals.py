from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import LiveBlogEntry
from .tasks import firebase_update_timestamp


@receiver([post_save, pre_delete], sender=LiveBlogEntry)
def update_entry(sender, instance, *args, **kwargs):
    """
    Notify Firebase with updated timestamp
    """
    firebase_update_timestamp.delay(instance.liveblog_id)

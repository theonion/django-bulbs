from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import LiveBlogEntry
from .tasks import firebase_delete_entry, firebase_update_entry


@receiver(pre_delete, sender=LiveBlogEntry)
def on_delete_entry(sender, instance, *args, **kwargs):
    firebase_delete_entry.delay(instance.id)


@receiver(post_save, sender=LiveBlogEntry)
def on_update_entry(sender, instance, *args, **kwargs):
    firebase_update_entry.delay(instance.id)

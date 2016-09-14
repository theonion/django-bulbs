from celery import shared_task
import requests

from django.conf import settings

from .models import LiveBlogEntry


# ----------------------------------------------------------------------
# Liveblog Firebase Strategy
#
# Firebase is used only as a messaging channel, to update clients when new entries are available.
#
# The idea is to cache a dictionary of {ENTRY_ID: PULBISH TIME} values for each LiveBlog, so clients
# will know when new content is available. Clients will then request only those Entry IDs that are
# currently published and they don't already have.
#
# Necessary to explicitly list each entry b/c future publish dates may roll over without triggering
# Firebase updates. This way our firebase logic can be dumb and only trigger on save/delete.
# ----------------------------------------------------------------------


def _get_endpoint():
    return getattr(settings, 'LIVEBLOG_FIREBASE_NOTIFY_ENDPOINT', None)


@shared_task(default_retry_delay=5)
def firebase_update_entry(entry_id):
    endpoint = _get_endpoint()
    if endpoint:
        entry = LiveBlogEntry.objects.get(id=entry_id)
        url = endpoint.format(liveblog_id=entry.liveblog.id,
                              entry_id=entry.id)
        if entry.published:
            resp = requests.patch(url, json={
                'published': entry.published.isoformat(),
            })
        else:
            resp = requests.delete(url)

        resp.raise_for_status()


@shared_task(default_retry_delay=5)
def firebase_delete_entry(entry_id):
    endpoint = _get_endpoint()
    if endpoint:
        entry = LiveBlogEntry.objects.get(id=entry_id)
        url = endpoint.format(liveblog_id=entry.liveblog.id,
                              entry_id=entry.id)
        resp = requests.delete(url)

        resp.raise_for_status()

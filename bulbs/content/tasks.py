from django.contrib.contenttypes.models import ContentType

from celery import task

@task
def index(content_type_id, pk, refresh=False):
    ctype = ContentType.objects.get_for_id(content_type_id)
    obj = ctype.get_object_for_this_type(pk=pk)
    obj.index(refresh=refresh)
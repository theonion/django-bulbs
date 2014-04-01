from elasticutils.contrib.django import get_es

from celery import shared_task


@shared_task(default_retry_delay=5)
def index(content_type_id, pk, refresh=False):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.model_class().objects.get(id=pk)
    obj.index(refresh=refresh)


@shared_task(default_retry_delay=10)
def update(pk, doc, refresh=False):
    from bulbs.content.models import Content
    obj = Content.objects.get(pk=pk)
    es = get_es()
    es.update(
        obj.index_name(),
        obj.get_mapping_type_name(),
        pk, doc=doc, refresh=refresh,
        retry_on_conflict=5)

from django.conf import settings

from elasticutils.contrib.django import get_es

from celery import task

@task(default_retry_delay=5)
def index(content_type_id, pk, refresh=False):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.model_class().objects.get(id=pk)
    obj.index(refresh=refresh)

@task(default_retry_delay=10)
def update(pk, doc, refresh=False):
    from bulbs.content.models import Content
    index = settings.ES_INDEXES.get('default')
    obj = Content.objects.get(pk=pk)
    es = get_es()
    es.update(index, obj.get_mapping_type_name(), pk, doc=doc, refresh=refresh, retry_on_conflict=5)
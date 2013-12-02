from django.conf import settings

from elasticutils.contrib.django import get_es

from celery import task

@task
def index(pk, refresh=False):
    from bulbs.content.models import Content
    obj = Content.objects.get(pk=pk)
    obj.index(refresh=refresh)

@task
def update(pk, doc, refresh=False):
    from bulbs.content.models import Content
    index = settings.ES_INDEXES.get('default')
    obj = Content.objects.get(pk=pk)
    es = get_es()
    es.update(index, obj.get_mapping_type_name(), pk, doc=doc, refresh=refresh)
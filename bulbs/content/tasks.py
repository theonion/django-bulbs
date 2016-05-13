from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task


@shared_task(default_retry_delay=5)
def index(content_type_id, pk, refresh=False):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.model_class().objects.get(id=pk)
    obj.index(refresh=refresh)


@shared_task(default_retry_delay=5)
def index_content_contributions(content_pk):
    from bulbs.contributions.models import Contribution
    for contribution in Contribution.objects.filter(content__pk=content_pk):
        contribution.save()


@shared_task(default_retry_delay=5)
def index_content_report_content_proxy(content_pk):
    from bulbs.contributions.models import ReportContent
    try:
        proxy = ReportContent.reference.get(id=content_pk)
        proxy.index()
    except ObjectDoesNotExist:
        pass


@shared_task(default_retry_delay=5)
def index_feature_type_content(featuretype_pk):
    from .models import FeatureType
    featuretype = FeatureType.objects.get(pk=featuretype_pk)
    for content in featuretype.content_set.all():
        content.index()

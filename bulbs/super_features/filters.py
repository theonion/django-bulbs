import django_filters
from rest_framework import filters

from bulbs.super_features.utils import get_superfeature_model

SUPERFEATURE_MODEL = get_superfeature_model()


def filter_status(queryset, value):
    if not value:
        return queryset
    else:
        # NOTE: this list comprehension is happening because
        # status is a property, not a model field
        # see: http://stackoverflow.com/a/1205416
        return [sf for sf in queryset
                if sf.status.lower() == value.lower()]


class SuperFeatureFilter(filters.FilterSet):
    status = django_filters.CharFilter(action=filter_status)

    class Meta:
        model = SUPERFEATURE_MODEL
        fields = ['status']

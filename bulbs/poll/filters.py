from django.utils import timezone

from elasticsearch_dsl.filter import Range


def Closed():  # noqa
    end_date_params = {
        "lte": timezone.now(),
    }

    return Range(end_date=end_date_params)

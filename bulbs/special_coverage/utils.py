"""Common utilities for special coverage behaviors."""
from django.conf import settings
from django.utils import timezone

from bulbs.content.filters import Published
from .models import SpecialCoverage
from .search import SearchParty


def get_sponsored_special_coverages():
    """:returns: Django query for all active special coverages with active campaigns."""
    now = timezone.now()
    return SpecialCoverage.objects.filter(
        tunic_campaign_id__isnull=False,
        start_date__lte=now,
        end_date__gt=now
    )


def get_sponsored_special_coverage_query(only_recent=False):
    """
    Reference to all SpecialCovearge queries.

    :param only_recent: references RECENT_SPONSORED_OFFSET_HOURS from django settings.
        Used to return sponsored content within a given configuration of hours.
    :returns: Djes.LazySearch query matching all active speical coverages.
    """
    special_coverages = get_sponsored_special_coverages()
    es_query = SearchParty(special_coverages).search()
    if only_recent:
        offset = getattr(settings, "RECENT_SPONSORED_OFFSET_HOURS", 0)
        es_query = es_query.filter(
            Published(after=timezone.now() - timezone.timedelta(hours=offset))
        )
    return es_query

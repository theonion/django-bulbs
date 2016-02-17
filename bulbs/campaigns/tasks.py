from celery import shared_task


@shared_task(default_retry_delay=5)
def save_campaign_special_coverage_percolator(campaign_pk):
    from bulbs.special_coverage.models import SpecialCoverage
    for special_coverage in SpecialCoverage.objects.filter(campaign_id=campaign_pk):
        special_coverage._save_percolator()

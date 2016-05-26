from celery import shared_task


@shared_task(default_retry_delay=5)
def save_campaign_special_coverage_percolator(tunic_campaign_id):
    from bulbs.special_coverage.models import SpecialCoverage
    for special_coverage in SpecialCoverage.objects.filter(tunic_campaign_id=tunic_campaign_id):
        special_coverage._save_percolator()

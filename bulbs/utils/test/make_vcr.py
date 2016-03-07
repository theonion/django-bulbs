import vcr
import os

from django.conf import settings


def make_vcr(test_path, record_mode='once'):
    base_dir = os.path.dirname(os.path.realpath(test_path))
    cassette_dir = os.path.join(base_dir, 'test_data', 'cassettes')

    return vcr.VCR(
        cassette_library_dir=cassette_dir,
        ignore_hosts=settings.ES_CONNECTIONS['default']['hosts'],
        record_mode=record_mode,
        filter_post_data_parameters=['access_token'],
        filter_query_parameters=['access_token']
    )

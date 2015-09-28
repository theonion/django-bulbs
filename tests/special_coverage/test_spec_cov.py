from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase


class SpecialCoverageModelTests(BaseIndexableTestCase):

    def test_config_load_save(self):
        # Basic load/save to verify flexible config format.
        CONFIG = {'one': True,
                  'two': {'three': [0, 1, 'two']}}
        special_coverage = SpecialCoverage.objects.create(id=1, config=CONFIG)
        self.assertEqual(SpecialCoverage.objects.get(id=1).config,
                         CONFIG)

    def test_default(self):
        self.assertEqual(SpecialCoverage.objects.create().config, {})

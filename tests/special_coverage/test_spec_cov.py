from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase


class SpecialCoverageModelTests(BaseIndexableTestCase):

    def test_config_load_save(self):
        # Basic load/save to verify flexible config format.
        config = {
            'one': True,
            'two': {'three': [0, 1, 'two']}
        }
        SpecialCoverage.objects.create(id=1, config=config)
        self.assertEqual(SpecialCoverage.objects.get(id=1).config,
                         config)

    def test_default(self):
        self.assertEqual(SpecialCoverage.objects.create().config, {})

    def test_save_video_none(self):
        sc = SpecialCoverage.objects.create(id=1, videos=[1, 2], name='god')
        self.assertEqual(sc.videos, [1, 2])
        sc = SpecialCoverage.objects.create(id=2, videos=[1, 2, None], name='not')
        self.assertEqual(sc.videos, [1, 2])
        sc = SpecialCoverage.objects.create(id=3, videos=['1', '2', 'dad'], name='dead')
        self.assertEqual(sc.videos, [1, 2])

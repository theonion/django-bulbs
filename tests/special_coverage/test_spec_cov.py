from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test.utils import override_settings

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.methods import today
from bulbs.utils.test import BaseIndexableTestCase


TODAY = today()


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

    def test_save_super_features(self):
        sc = SpecialCoverage.objects.create(id=1, super_features=[1, 2], name='god')
        self.assertEqual(sc.super_features, [1, 2])
        sc = SpecialCoverage.objects.create(id=2, super_features=[1, 2, None], name='not')
        self.assertEqual(sc.super_features, [1, 2])
        sc = SpecialCoverage.objects.create(id=3, super_features=['1', '2', 'dad'], name='dead')
        self.assertEqual(sc.super_features, [1, 2])

    def test_start_and_end_validation(self):
        sc = SpecialCoverage.objects.create(
            name="God",
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        sc.save()
        self.assertTrue(sc.is_active)

        with self.assertRaises(ValidationError):
            sc = SpecialCoverage.objects.create(name="Is", end_date=timezone.now())

        with self.assertRaises(ValidationError):
            sc = SpecialCoverage.objects.create(
                name="Is",
                start_date=timezone.now(),
                end_date=timezone.now() - timezone.timedelta(days=10)
            )

    @override_settings(TODAY=TODAY.date())
    def test_is_active_date_configuration(self):
        sc = SpecialCoverage.objects.create(
            name="God",
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        self.assertTrue(sc.is_active)

    @override_settings(TODAY=TODAY.date())
    def test_is_active_without_end_date(self):
        sc = SpecialCoverage.objects.create(
            name="God",
            start_date=timezone.now() - timezone.timedelta(days=10)
        )
        self.assertTrue(sc.is_active)

    def test_custom_template_default(self):
        sc = SpecialCoverage.objects.create(
            name="Kill Me Now",
            start_date=timezone.now() - timezone.timedelta(days=5),
            end_date=timezone.now() + timezone.timedelta(days=5)
        )
        self.assertEqual(
            sc.custom_template_name, "special_coverage/custom/kill_me_now_custom.html"
        )

    @override_settings(CUSTOM_SPECIAL_COVERAGE_PATH=None)
    def test_custom_template_name_no_root(self):
        sc = SpecialCoverage.objects.create(name="Kill Me Now")
        self.assertEqual(sc.custom_template_name, "kill_me_now_custom.html")

    @override_settings(CUSTOM_SPECIAL_COVERAGE_PATH="templates/garbage")
    def test_custom_template_name_custom_path(self):
        sc = SpecialCoverage.objects.create(name="Kill Me Now")
        self.assertEqual(
            sc.custom_template_name, "templates/garbage/kill_me_now_custom.html"
        )

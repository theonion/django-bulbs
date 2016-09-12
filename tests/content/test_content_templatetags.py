from django.template import Context, Template, TemplateSyntaxError
from django.test import override_settings

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.content.templatetags.content import campaign_display_preamble


TEST_TUNIC_BACKEND_ROOT = "//my.tunic.url"
TEST_TUNIC_API_PATH = "/api/path/"


@override_settings(
    TUNIC_BACKEND_ROOT=TEST_TUNIC_BACKEND_ROOT,
    TUNIC_API_PATH=TEST_TUNIC_API_PATH,
)
class ContentTemplateTagTunicCampaignUrlTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentTemplateTagTunicCampaignUrlTestCase, self).setUp()

        self.campaign_id = 1

    def test_content_tunic_campaign_url(self):
        """Test how template renders with an id."""

        renderer = Template(
            "{{% load content %}}{{% content_tunic_campaign_url {} %}}".format(
                self.campaign_id
            )
        )
        self.assertEquals(
            renderer.render(Context({})),
            "{}{}campaign/{}/public".format(
                TEST_TUNIC_BACKEND_ROOT,
                TEST_TUNIC_API_PATH,
                self.campaign_id
            )
        )

    def test_content_tunic_campaign_url_no_id(self):
        """Template should error out if no id was given."""

        with self.assertRaises(TemplateSyntaxError):
            Template("{% load content %}{% content_tunic_campaign_url %}")

    def test_content_tunic_campaign_url_ratio_param(self):
        """Template should request with a ratio param if given."""

        image_ratio = "3x1"

        renderer = Template(
            "{{% load content %}}{{% content_tunic_campaign_url {} image_ratio='{}' %}}".format(
                self.campaign_id,
                image_ratio
            )
        )
        self.assertEquals(
            renderer.render(Context({})),
            "{}{}campaign/{}/public?image_ratio={}".format(
                TEST_TUNIC_BACKEND_ROOT,
                TEST_TUNIC_API_PATH,
                self.campaign_id,
                image_ratio
            )
        )

    def test_content_tunic_campaign_url_width_param(self):
        """Template should request with a width param if given."""

        image_width = 300

        renderer = Template(
            "{{% load content %}}{{% content_tunic_campaign_url {} image_width={} %}}".format(
                self.campaign_id,
                image_width
            )
        )
        self.assertEquals(
            renderer.render(Context({})),
            "{}{}campaign/{}/public?image_width={}".format(
                TEST_TUNIC_BACKEND_ROOT,
                TEST_TUNIC_API_PATH,
                self.campaign_id,
                image_width
            )
        )

    def test_content_tunic_campaign_url_format_param(self):
        """Template should request with a format param if given."""

        image_format = "png"

        renderer = Template(
            "{{% load content %}}{{% content_tunic_campaign_url {} image_format='{}' %}}".format(
                self.campaign_id,
                image_format
            )
        )
        self.assertEquals(
            renderer.render(Context({})),
            "{}{}campaign/{}/public?image_format={}".format(
                TEST_TUNIC_BACKEND_ROOT,
                TEST_TUNIC_API_PATH,
                self.campaign_id,
                image_format
            )
        )


class ContentTemplateTagTunicCampaignDisplayPreamble(BaseIndexableTestCase):
    def setUp(self):
        super(ContentTemplateTagTunicCampaignDisplayPreamble, self).setUp()

    def test_campaign_display_preamble_whitelisted_id(self):
        response = campaign_display_preamble(563)
        expected_response = "Sponsored by"

        self.assertEquals(response, expected_response)

    def test_campaign_display_preamble_non_whitelisted_id(self):
        response = campaign_display_preamble(1)
        expected_response = "Presented by"

        self.assertEquals(response, expected_response)

from django.template import Context, Template, TemplateSyntaxError
from django.test import override_settings

from bulbs.utils.test import BaseIndexableTestCase


TEST_TUNIC_BACKEND_ROOT = "//my.tunic.url"
TEST_TUNIC_API_PATH = "/api/path/"


class ContentTemplateTagsTestCase(BaseIndexableTestCase):

    @override_settings(
        TUNIC_BACKEND_ROOT=TEST_TUNIC_BACKEND_ROOT,
        TUNIC_API_PATH=TEST_TUNIC_API_PATH,
    )
    def test_content_tunic_campaign_url(self):
        """Test how template renders with an id."""

        campaign_id = 1

        t = Template("{{% load content %}}{{% content_tunic_campaign_url {} %}}".format(campaign_id))
        c = Context({})
        self.assertEquals(t.render(c), "{}{}/{}/public".format(
            TEST_TUNIC_BACKEND_ROOT,
            TEST_TUNIC_API_PATH,
            campaign_id
        ))

    def test_content_tunic_campaign_url_no_id(self):
        """Template should error out if no id was given."""

        with self.assertRaises(TemplateSyntaxError):
            Template("{% load content %}{% content_tunic_campaign_url %}")

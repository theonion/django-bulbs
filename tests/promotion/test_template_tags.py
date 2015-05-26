import datetime

from django.template import Template, Context
from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase

from bulbs.promotion.models import PZone, InsertOperation
from bulbs.utils.test import make_content


class ForPZoneTestCase(BaseIndexableTestCase):
    def setUp(self):
        super(ForPZoneTestCase, self).setUp()
        self.pzone = PZone.objects.create(name="homepage", zone_length=5)
        data = []
        for i in range(6):
            content = make_content(title="Content test #{}".format(i), )
            data.append({"id": content.pk})

        self.pzone.data = data
        self.pzone.save()

    def test_simple_tag(self):

        t = Template("""{% load promotion %}{% forpzone name="homepage" %}{{ content.title }} | {% endforpzone %}""")
        c = Context({})
        self.assertEquals(t.render(c), "Content test #0 | Content test #1 | Content test #2 | Content test #3 | Content test #4 | ")

    def test_pzone_tag_with_slice(self):
        t = Template("""{% load promotion %}{% forpzone name="homepage" slice=":2" %}{{ content.title }} | {% endforpzone %}""")
        c = Context({})
        self.assertEquals(t.render(c), "Content test #0 | Content test #1 | ")

    def test_pzone_preview(self):
        test_time = timezone.now() + datetime.timedelta(hours=1)
        new_content = make_content(published=test_time, title="Something New")
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content
        )

        t = Template("""{% load promotion %}{% forpzone name="homepage" %}{{ content.title }} | {% endforpzone %}""")
        c = Context({})
        self.assertEquals(t.render(c), "Content test #0 | Content test #1 | Content test #2 | Content test #3 | Content test #4 | ")

        c = Context({"pzone_preview": test_time + datetime.timedelta(minutes=30)})
        self.assertEquals(t.render(c), "Something New | Content test #0 | Content test #1 | Content test #2 | Content test #3 | ")

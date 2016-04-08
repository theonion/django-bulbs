from django.test import override_settings
from django.utils import timezone

from bulbs.content.models import Content
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj, TestContentObjTwo, TestReadingListObj


class ContentManagerTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentManagerTestCase, self).setUp()
        make_content(TestReadingListObj, evergreen=True, published=timezone.now(), _quantity=50)
        make_content(TestContentObj, published=timezone.now(), _quantity=50)
        Content.search_objects.refresh()

    def test_sponsored(self):
        sponsored = Content.search_objects.sponsored().extra(from_=0, size=50)
        qs = TestContentObj.objects.filter(tunic_campaign_id__isnull=False)
        self.assertEqual(qs.count(), sponsored.count())
        self.assertEqual(
            sorted([obj.id for obj in qs]),
            sorted([obj.id for obj in sponsored])
        )

    def test_evergreen(self):
        evergreen = Content.search_objects.evergreen().extra(from_=0, size=50)
        qs = Content.objects.filter(evergreen=True)
        self.assertEqual(qs.count(), evergreen.count())
        self.assertEqual(
            sorted([obj.id for obj in qs]),
            sorted([obj.id for obj in evergreen])
        )

    @override_settings(VIDEO_DOC_TYPE=TestContentObjTwo.search_objects.mapping.doc_type)
    def test_evergreen_video(self):
        make_content(TestContentObjTwo, evergreen=True, published=self.now, _quantity=12)
        make_content(TestContentObjTwo, published=self.now, _quantity=12)
        Content.search_objects.refresh()
        evergreen = Content.search_objects.evergreen_video().extra(from_=0, size=50)
        qs = TestContentObjTwo.objects.filter(evergreen=True)
        self.assertEqual(12, evergreen.count())
        self.assertEqual(
            sorted([obj.id for obj in qs]),
            sorted([obj.id for obj in evergreen])
        )

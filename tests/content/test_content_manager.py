from django.utils import timezone

from bulbs.content.models import Content, FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import (TestContentObj, TestReadingListObj, TestVideoContentObj)

from bulbs.videos.models import VideohubVideo


class ContentManagerTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentManagerTestCase, self).setUp()
        self.instant_feature_type = FeatureType.objects.create(
            name="Da Gahbage", instant_article=True
        )
        self.feature_type = FeatureType.objects.create(
            name="Insult corner", instant_article=False
        )

        make_content(
            TestReadingListObj,
            feature_type=self.instant_feature_type,
            evergreen=True,
            published=timezone.now(),
            _quantity=50
        )
        make_content(
            TestContentObj,
            feature_type=self.feature_type,
            published=timezone.now(),
            _quantity=50
        )
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

    def test_instant_articles(self):
        instant_articles = Content.search_objects.instant_articles()
        self.assertEqual(instant_articles.count(), 50)
        self.assertTrue(instant_articles[0].feature_type.instant_article)

    def test_evergreen_video(self):
        videohub_ref = VideohubVideo.objects.create(id=1)
        expected = make_content(TestVideoContentObj, videohub_ref=videohub_ref, evergreen=True,
                                published=self.now, _quantity=12)
        # Ignored content
        make_content(TestVideoContentObj, videohub_ref=videohub_ref,
                     published=self.now, _quantity=12)  # Not evergreen
        make_content(TestVideoContentObj, evergreen=True, published=self.now)  # No video ref

        Content.search_objects.refresh()
        evergreen = Content.search_objects.evergreen_video()[:50]
        self.assertEqual(12, evergreen.count())
        self.assertEqual(
            sorted([o.id for o in expected]),
            sorted([o.id for o in evergreen])
        )

    def test_videos(self):
        videohub_ref = VideohubVideo.objects.create(id=1)
        expected = [make_content(TestVideoContentObj, videohub_ref=videohub_ref,
                                 published=self.now - timezone.timedelta(hours=hours))
                    for hours in [4, 2, 3, 0, 5, 1]]
        # Ignored content
        make_content(TestVideoContentObj, videohub_ref=videohub_ref)  # Not published
        make_content(TestVideoContentObj, videohub_ref=videohub_ref,
                     published=(self.now + timezone.timedelta(hours=1)))  # Not published yet
        make_content(TestVideoContentObj, published=self.now)  # No video ref

        Content.search_objects.refresh()
        recent = Content.search_objects.videos()
        self.assertEqual([o.id for o in sorted(expected, reverse=True, key=lambda x: x.published)],
                         [o.id for o in recent])

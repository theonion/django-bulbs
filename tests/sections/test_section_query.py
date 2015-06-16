from django.utils import timezone

from bulbs.content.models import Content, Tag
from bulbs.sections.models import Section
from bulbs.utils.test import BaseIndexableTestCase, make_content


class BaseCustomSearchFilterTests(BaseIndexableTestCase):
    def setUp(self):
        super(BaseCustomSearchFilterTests, self).setUp()
        section_type_names = (
            "Video", "Politics", "Sports", "Local", "Business", "Entertainment",
            "Science & Technology",
        )
        
        tags = []
        for name in section_type_names:
            tags.append(Tag.objects.create(name=name))

        content_data = (
            dict(
                title="Must watch",
                tags=[0,],
            ),
            dict(
                title="I can't bloody believe Mitt Romney dang it!",
                tags=[1,],
            ),
            dict(
                title="Jebbin it",
                tags=[1,],
            ),
            dict(
                title="Derrick Rose found healthy",
                tags=[2,],
            ),
            dict(
                title="Chill Area Man",
                tags=[3,],
            ),
            dict(
                title="Exelon goes green",
                tags=[4,],
            ),
            dict(
                title="Koch Brothers fund area man's rock opera",
                tags=[3, 4]
            ),
            dict(
                title="Shania Twain unimpressed",
                tags=[5,],
            ),
            dict(
                title="Tiny microbug",
                tags=[6,],
            ),
        )

        publish_offset = timezone.timedelta(hours=1)
        published = timezone.now() + timezone.timedelta(days=5)
        content_list = []
        queries = {}
        for data in content_data:
            data["published"] = published
            data["tags"] = [tags[tag_index] for tag_index in data.pop("tags")]
            content = make_content(**data)
            content_list.append(content)
            content.index()
            published -= publish_offset

            for t in data['tags']:
                query = {
                    'label': t.name,
                    'query': {
                        'groups': [
                            {
                                'conditions': [
                                    {
                                        'type': 'all',
                                        'field': 'tag',
                                        'values': [
                                            {
                                                'value': t.slug,
                                                'label': t.slug
                                            }
                                        ]
                                    }         
                                ]
                            },
                        ]
                    }
                }
                if query['label'] in queries:
                    queries[query['label']]['count'] += 1
                else:
                    queries[query['label']] = {
                        'query': query,
                        'count': 1
                    }

        self.queries = queries
        self.content_list = content_list
        self.tags = tags
        Content.search_objects.refresh()


class SectionQueryTests(BaseCustomSearchFilterTests):

    def setUp(self):
        super(SectionQueryTests, self).setUp()

    def test_get_content(self):
        query = self.queries['Video']['query']
        section = Section.objects.create(
            name="Video",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 1)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Politics']['query']
        section = Section.objects.create(
            name="Politics",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 2)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Sports']['query']
        section = Section.objects.create(
            name="Sports",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 1)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Local']['query']
        section = Section.objects.create(
            name="Local",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 2)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Business']['query']
        section = Section.objects.create(
            name="Business",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 2)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Entertainment']['query']
        section = Section.objects.create(
            name="Entertainment",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 1)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())

        query = self.queries['Science & Technology']['query']
        section = Section.objects.create(
            name="Science & Technology",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), 1)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())
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
        queries = []
        for data in content_data:
            data["published"] = published
            data["tags"] = [tags[tag_index] for tag_index in data.pop("tags")]
            content = make_content(**data)
            content_list.append(content)
            content.index()
            published -= publish_offset

            query = {
                'label': data['tags'][0].name,
                'query': {
                    'groups': [
                        {
                            'conditions': [
                                {
                                    'type': 'all',
                                    'field': 'tag',
                                    'values': [
                                        {
                                            'value': data['tags'][0].slug,
                                            'label': data['tags'][0].slug
                                        }
                                    ]
                                }         
                            ]
                        },
                    ]
                }
            }
            queries.append(query)

        self.content_list = content_list
        self.tags = tags
        Content.search_objects.refresh()

        search_list = [(q, 1) for q in queries]
        self.search_expectations = tuple(search_list)


class SectionQueryTests(BaseCustomSearchFilterTests):

    def setUp(self):
        super(SectionQueryTests, self).setUp()

    def test_get_content(self):
        query, count = self.search_expectations[1]
        section = Section.objects.create(
            name="Video",
            description="meh",
            query = query
        
        )
        res = section.get_content()
        self.assertEqual(res.count(), count)
        tag_name = query['label']
        tag = Tag.objects.get(name=tag_name)
        self.assertIn(tag, res[0].tags.all())
        
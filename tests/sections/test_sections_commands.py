from django.core.management import call_command

from elasticsearch.exceptions import TransportError
from model_mommy import mommy

from bulbs.content.models import Content
from bulbs.sections.models import Section
from bulbs.utils.test import BaseIndexableTestCase

class CommandsTestCase(BaseIndexableTestCase):
    def test_index_sections(self):
        """Tests the command located in `index_sections.py`
        """

        for i in range(50):
            section_name = 'Section-{}'.format(i)
            section_slug = 'section-{}'.format(i)
            query = {
                'label': section_name,
                'query': {
                    'groups': [
                        {
                            'conditions': [
                                {
                                    'type': 'all',
                                    'field': 'tag',
                                    'values': [
                                        {
                                            'value': section_slug,
                                            'label': section_name
                                        }
                                    ]
                                }

                            ]
                        }
                    ]
                }
            }
            Section.objects.create(name=section_name, query=query)

        assert Section.objects.count() == 50
        with self.assertRaises(TransportError):
            section = Section.objects.first()
            _id = "{}.{}".format(section.name, section.id)
            self.es.get(
                index=Content.search_objects.mapping.index,
                doc_type='.percolator',
                id=_id
            )

        empty_sections = mommy.make(Section, _quantity=50)
        db_empty_section_ids = [s.id for s in Section.objects.all() if s.query == {} or s.query is None]
        
        assert len(db_empty_section_ids) == len(empty_sections)
        with self.assertRaises(TransportError):
            section = empty_sections[0]
            _id = "{}.{}".format(section.name, section.query)
            self.es.get(
                index=Content.search_objects.mapping.index,
                doc_type='.percolator',
                id=_id,
            )        

        call_command('index_sections')
        query_sections = Section.objects.exclude(id__in=db_empty_section_ids)

        for section in query_sections:
            response = self.es.get(
                index=Content.search_objects.mapping.index,
                doc_type='.percolator',
                id=section.es_id
            )
            assert response['found']
            assert response['_id'] == section.es_id
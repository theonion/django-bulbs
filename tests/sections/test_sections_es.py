from django.utils import timezone

from bulbs.content.models import Content
from bulbs.sections.models import Section
from bulbs.utils.test import BaseIndexableTestCase

class SpecialCoverageQueryTests(BaseIndexableTestCase):

    def setUp(self):
        super(SpecialCoverageQueryTests, self).setUp()

    def test_es_id(self):
        section = Section.objects.create(name='Politics', id=666)
        assert section.es_id == "politics.666"

    def test_save_percolator(self):
        politics_condition = {
            "values": [{
                "value": "politics",
                "label": "Politics",
            }],
            "type": "all",
            "field": "tag",
        }
        query = {
            "label": "Politics",
            "query": {
                "groups": [{"conditions": [politics_condition]}]
            },
        }

        section = Section.objects.create(name="Politics", query=query, id=777)
        section._save_percolator()

        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="politics.777",
        )
        assert response["_source"]["query"] == section.get_content().to_dict()["query"]


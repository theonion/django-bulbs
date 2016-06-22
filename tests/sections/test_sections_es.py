from elasticsearch.exceptions import TransportError

from bulbs.content.models import Content
from bulbs.sections.models import Section
from bulbs.utils.test import BaseIndexableTestCase


class SpecialCoverageQueryTests(BaseIndexableTestCase):

    def setUp(self):
        super(SpecialCoverageQueryTests, self).setUp()

    def test_es_id(self):
        section = Section.objects.create(name='Politics', id=666)
        assert section.es_id == "section.666"

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
            id="section.777",
        )
        assert response["_source"]["query"] == section.get_content().to_dict()["query"]

        # Update the query
        sports_condition = {
            "values": [{
                "value": "sports",
                "label": "Sports",
            }],
            "type": "all",
            "field": "tag",
        }
        section.query = {
            "label": "Sports",
            "query": {
                "groups": [{
                    "conditions": [sports_condition],
                }]
            },
        }
        section._save_percolator()

        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="section.777"
        )
        assert response["_source"]["query"] == section.get_content().to_dict()["query"]

    def test_delete_percolator(self):
        section = Section.objects.create(name="Business", id=999)
        self.es.index(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="section.999",
            body={
                "query": {
                    "filtered": {
                        "filter": {
                            "match_all": {}
                        }
                    }
                }
            }
        )
        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="section.999"
        )
        assert isinstance(response, dict)
        assert response["_id"] == "section.999"

        section.delete()

        with self.assertRaises(TransportError):
            response = self.es.get(
                index=Content.search_objects.mapping.index,
                doc_type=".percolator",
                id="section.999"
            )

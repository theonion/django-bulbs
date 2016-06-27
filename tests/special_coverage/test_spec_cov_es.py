from datetime import timedelta

from django.utils import timezone
from elasticsearch.exceptions import TransportError

from bulbs.content.models import Content
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase


class SpecialCoverageQueryTests(BaseIndexableTestCase):

    def test_es_id(self):
        sc = SpecialCoverage(
            id=101,
            name="All Obama, Baby",
            description="All Obama, Baby"
        )
        assert sc.es_id == "specialcoverage.101"

    def test_save_percolator(self):
        joe_biden_condition = {
            "values": [{
                "value": "joe-biden",
                "label": "Joe Biden"
            }],
            "type": "all",
            "field": "tag"
        }
        query = {
            "label": "Uncle Joe",
            "query": {
                "groups": [{
                    "conditions": [joe_biden_condition]
                }]
            },
        }

        sc = SpecialCoverage(
            id=93,
            name="Uncle Joe",
            description="Classic Joeseph Biden",
            query=query
        )

        # Manually index this percolator
        sc._save_percolator()

        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="specialcoverage.93"
        )

        sc_query = sc.get_content(published=False).to_dict()["query"]
        assert response["_source"]["query"] == sc_query

        # Now let's update the query
        obama_condition = {
            "values": [{
                "value": "barack-obama",
                "label": "Barack Obama"
            }],
            "type": "all",
            "field": "tag"
        }
        sc.query = {
            "label": "Barack",
            "query": {
                "groups": [{
                    "conditions": [obama_condition]
                }]
            },
        }
        sc._save_percolator()

        # Did the query change take?
        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        # Shutting up publishing

        sc_query = sc.get_content(published=False).to_dict()["query"]
        assert response["_source"]["query"] == sc_query

    def test_delete_percolator(self):
        sc = SpecialCoverage(
            id=93,
            name="Uncle Joe",
            description="Classic Joeseph Biden"
        )
        self.es.index(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="specialcoverage.93",
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
            id="specialcoverage.93"
        )
        assert isinstance(response, dict)
        assert response["_id"] == "specialcoverage.93"

        sc.delete()

        with self.assertRaises(TransportError):
            response = self.es.get(
                index=Content.search_objects.mapping.index,
                doc_type=".percolator",
                id="specialcoverage.93"
            )

    def test_sponsored_special_coverage(self):
        joe_biden_condition = {
            "values": [{
                "value": "joe-biden",
                "label": "Joe Biden"
            }],
            "type": "all",
            "field": "tag"
        }
        query = {
            "label": "Uncle Joe",
            "query": {
                "groups": [{
                    "conditions": [joe_biden_condition]
                }]
            },
        }

        yesterday = timezone.now() - timedelta(days=1)
        tomorrow = timezone.now() + timedelta(days=1)

        sc = SpecialCoverage(
            id=93,
            name="Uncle Joe",
            description="Classic Joeseph Biden",
            query=query,
            start_date=yesterday,
            end_date=tomorrow,
            tunic_campaign_id=1
        )
        sc._save_percolator()

        response = self.es.get(
            index=Content.search_objects.mapping.index,
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        assert response["_source"].get("sponsored")is True
        assert response["_source"]["start_date"] == yesterday.isoformat()
        assert response["_source"]["end_date"] == tomorrow.isoformat()

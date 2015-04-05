from datetime import timedelta

from django.utils import timezone
from elasticsearch.exceptions import TransportError
from elastimorphic.tests.base import BaseIndexableTestCase
from model_mommy import mommy

from bulbs.content.models import Content, FeatureType, Tag
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import make_content

from example.testcontent.models import TestContentObjTwo


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
            index=Content.get_index_name(),
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        assert response["_source"]["query"]["filtered"]["filter"] == sc.get_content().build_search()["filter"]

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
            index=Content.get_index_name(),
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        assert response["_source"]["query"]["filtered"]["filter"] == sc.get_content().build_search()["filter"]

    def test_delete_percolator(self):
        sc = SpecialCoverage(
            id=93,
            name="Uncle Joe",
            description="Classic Joeseph Biden"
        )
        self.es.index(
            index=Content.get_index_name(),
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
            index=Content.get_index_name(),
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        assert isinstance(response, dict)
        assert response["_id"] == "specialcoverage.93"

        sc._delete_percolator()

        with self.assertRaises(TransportError):
            response = self.es.get(
                index=Content.get_index_name(),
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
        campaign = mommy.make("campaigns.Campaign", start_date=yesterday, end_date=tomorrow)

        sc = SpecialCoverage(
            id=93,
            name="Uncle Joe",
            description="Classic Joeseph Biden",
            query=query,
            campaign=campaign,
        )
        sc._save_percolator()

        response = self.es.get(
            index=Content.get_index_name(),
            doc_type=".percolator",
            id="specialcoverage.93"
        )
        assert response["_source"].get("sponsored") == True
        assert response["_source"]["start_date"] == yesterday.isoformat()
        assert response["_source"]["end_date"] == tomorrow.isoformat()


from bulbs.special_coverage.models import SpecialCoverage

from tests.content.test_custom_search import BaseCustomSearchFilterTests


class SpecialCoverageQueryTests(BaseCustomSearchFilterTests):
    def setUp(self):
        super(SpecialCoverageQueryTests, self).setUp()

    def test_get_doc_type(self):
        assert SpecialCoverage.get_doc_type() == ".percolator"

    def test_es_id(self):
        sc = SpecialCoverage.objects.create(
            name="All Obama, Baby",
            description="All Obama, Baby"
        )
        es_id = "specialcoverage.{}".format(sc.id)
        assert sc.es_id == es_id

    def test_save_percolator(self):
        query = self.search_expectations[1][0]
        sc = SpecialCoverage.objects.create(
            name="All Obama, Baby",
            description="All Obama, Baby",
            query=query
        )
        res = sc._save_percolator()
        assert isinstance(res, dict)

    def test_delete_percolator(self):
        query = self.search_expectations[1][0]
        sc = SpecialCoverage.objects.create(
            name="All Obama, Baby",
            description="All Obama, Baby",
            query=query
        )
        res = sc._save_percolator()
        assert isinstance(res, dict)
        res = sc._delete_percolator()
        assert isinstance(res, dict)

from djes.models import IndexableManager


class SectionManager(IndexableManager):

    def get_by_identifier(self, identifier):
        identifier_id = identifier.split(".")[-1]
        return self.get(id=identifier_id)

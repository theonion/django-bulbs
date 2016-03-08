from collections import OrderedDict

from django.conf import settings


class SearchSlicer(object):
    """We want to search things like a seesaw. take that mike parent.
    """
    def __init__(self, *args, **kwargs):
        self.default_queryset = None
        self.querysets = OrderedDict()
        self.index = 0
        self.limit = kwargs.get("limit", getattr(settings, "READING_LIST_LIMIT", 100))

    def __iter__(self):
        return self

    def next(self):
        if self.index >= self.limit:
            raise StopIteration
        for validator, queryset in self.querysets.items():
            if validator(self.index):
                try:
                    result = queryset.next()
                    self.index += 1
                    return result
                except StopIteration:
                    pass
        result = self.default_queryset.next()
        self.index += 1
        return result

    def __next__(self):
        return self.next()

    def register_queryset(self, queryset, validator=None, default=False):
        """
        Add a given queryset to the iterator with custom logic for iteration.

        :param queryset: List of objects included in the reading list.
        :param validator: Custom logic to determine a queryset's position in a reading_list.
            Validators must accept an index as an argument and return a truthy value.
        :param default: Sets the given queryset as the primary queryset when no validator applies.
        """
        if default or self.default_queryset is None:
            self.default_queryset = queryset
            return
        if validator:
            self.querysets[validator] = queryset
        else:
            raise ValueError(
                """Querysets require validation logic to integrate with reading lists."""
            )


def FirstSlotSlicer(primary_query, secondary_query, limit=30):  # noqa
    """
    Inject the first object from a queryset into the first position of a reading list.

    :param primary_queryset: djes.LazySearch object. Default queryset for reading list.
    :param secondary_queryset: djes.LazySearch object. first result leads the reading_list.
    :return list: mixed reading list.
    """
    reading_list = SearchSlicer(limit=limit)
    reading_list.register_queryset(primary_query)
    reading_list.register_queryset(secondary_query, validator=lambda x: bool(x == 0))
    return reading_list

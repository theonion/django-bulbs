"""Custom search function to assist in customizing our special coverage searches."""
import six


def second_slot_query_generator(query1, query2):
    """Returns the result of a different query at the 1st index of iteration.

    :param query1: Primary search that will be the default result set.
    :type  query1: Any iterable object; intended for djes.search.LazySearch and django.Querysets.
    :param query2: Secondard search that will return at the 1st index of iteration.
    :type  query2: Any iterable object; intended for djes.search.LazySearch and django.Querysets.
    """
    index = 0
    while True:
        result = None
        if index == 1:
            try:
                result = six.next(query2)
            except IndexError:
                pass
        if result is None:
            try:
                result = six.next(query1)
            except IndexError:
                break
        yield result
        index += 1

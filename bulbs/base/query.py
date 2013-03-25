import rawes
import logging

from django.utils import timezone
from django.conf import settings


class ElasticSearchQuery(object):
    def __init__(self, published=True, content_type=None, tags=[]):

        if published is True:
            self.published = {
                'range': {
                    'published': {
                        'to': timezone.now(),
                    }
                }
            }
        if published is False:
            self.published = {
                'range': {
                    'published': {
                        'from': timezone.now(),
                    }
                }
            }
        # TODO: Test for datetime

        # TODO: Test for actual Tag() objects
        self.tags = []
        for tag in tags:
            self.tags.append({
                'term': {
                    "tag": tag,
                }
            })

        self.content_type = None
        if type(content_type) is str:
            self._content_type = {
                'term': {
                    'content_type': content_type
                }
            }
        elif content_type is not None:
            self.content_type = {
                'terms': {
                    'content_type': content_type,
                    'minimum_match': 1
                }
            }

    def set_limits(self, low=None, high=None):
        """Restricts the query by altering either the start, end or both offsets."""
        if low is not None:
            self.start_offset = int(low)

        if high is not None:
            self.end_offset = int(high)

    def clear_limits(self):
        """Clears any existing limits."""
        self.start_offset, self.end_offset = 0, None

    def data(self):
        must = []
        if self.published:
            must.append(self.published)

        if self.tags:
            must.append(self.tags)

        if self.content_type:
            must.append(self.content_type)

        search_data = {
            'query': {
                'bool': {
                    'must': must
                },
            }
        }
        return search_data


class ElasticQuerySet(object):
    """
    Provides a way to specify search parameters and lazily load results.

    Supports chaining (a la QuerySet) to narrow the search.
    """
    def __init__(self, model, query=None):
        # ``_using`` should only ever be a value other than ``None`` if it's
        # been forced with the ``.using`` method.
        self._es = rawes.Elastic(**settings.ES_SERVER)
        self.query = None

        # If ``query`` is present, it should override even what the routers
        # think.
        if query is not None:
            self.query = query

        self.model = model
        self._result_cache = []
        self._result_count = None
        self._cache_full = False
        self._load_all = False
        self.log = logging.getLogger('haystack')

    def __repr__(self):
        REPR_OUTPUT_SIZE = 25
        data = list(self[:REPR_OUTPUT_SIZE])

        if len(self) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."

        return repr(data)

    def __len__(self):
        if not self._result_count:
            self._result_count = self.query.get_count()
            return self._result_count
            # Some backends give weird, false-y values here. Convert to zero.
            if not self._result_count:
                self._result_count = 0

        # This needs to return the actual number of hits, not what's in the cache.
        return self._result_count

    def __iter__(self):
        if self._cache_is_full():
            # We've got a fully populated cache. Let Python do the hard work.
            return iter(self._result_cache)

        return self._manual_iter()

    def _cache_is_full(self):
        if not self.query.has_run():
            return False

        if len(self) <= 0:
            return True

        try:
            self._result_cache.index(None)
            return False
        except ValueError:
            # No ``None``s found in the results. Check the length of the cache.
            return len(self._result_cache) > 0

    def _manual_iter(self):
        ITERATOR_LOAD_PER_QUERY = 25

        # If we're here, our cache isn't fully populated.
        # For efficiency, fill the cache as we go if we run out of results.
        # Also, this can't be part of the __iter__ method due to Python's rules
        # about generator functions.
        current_position = 0
        current_cache_max = 0

        while True:
            if len(self._result_cache) > 0:
                try:
                    current_cache_max = self._result_cache.index(None)
                except ValueError:
                    current_cache_max = len(self._result_cache)

            while current_position < current_cache_max:
                yield self._result_cache[current_position]
                current_position += 1

            if self._cache_is_full():
                raise StopIteration

            # We've run out of results and haven't hit our limit.
            # Fill more of the cache.
            if self._fill_cache(current_position, current_position + ITERATOR_LOAD_PER_QUERY) is False:
                raise StopIteration

    def _fill_cache(self, start, end, **kwargs):
        # Tell the query where to start from and how many we'd like.
        self.query._reset()
        self.query.set_limits(start, end)
        results = self.query.get_results(**kwargs)

        if results is None or len(results) == 0:
            return False

        # Setup the full cache now that we know how many results there are.
        # We need the ``None``s as placeholders to know what parts of the
        # cache we have/haven't filled.
        # Using ``None`` like this takes up very little memory. In testing,
        # an array of 100,000 ``None``s consumed less than .5 Mb, which ought
        # to be an acceptable loss for consistent and more efficient caching.
        if len(self._result_cache) == 0:
            self._result_cache = [None for i in xrange(self.query.get_count())]

        if start is None:
            start = 0

        if end is None:
            end = self.query.get_count()

        to_cache = self.post_process_results(results)

        # Assign by slice.
        self._result_cache[start:start + len(to_cache)] = to_cache
        return True

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice, int, long)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
                "Negative indexing is not supported."

        # Remember if it's a slice or not. We're going to treat everything as
        # a slice to simply the logic and will `.pop()` at the end as needed.
        if isinstance(k, slice):
            is_slice = True
            start = k.start

            if k.stop is not None:
                bound = int(k.stop)
            else:
                bound = None
        else:
            is_slice = False
            start = k
            bound = k + 1

        # We need check to see if we need to populate more of the cache.
        if len(self._result_cache) <= 0 or (None in self._result_cache[start:bound] and not self._cache_is_full()):
            try:
                self._fill_cache(start, bound)
            except StopIteration:
                # There's nothing left, even though the bound is higher.
                pass

        # Cache should be full enough for our needs.
        if is_slice:
            return self._result_cache[start:bound]
        else:
            return self._result_cache[start]

    def post_process_results(self, results):
        to_cache = []

        for result in results:
            content = self.model()
            content.pk = result['_id']
            for key, value in result['_source'].items():
                if key == "content_type":
                    app_label, model = value.split("-")
                    content_type = ContentType.objects.get(app_label=app_label, model=model)
                    content.content_type = content_type
                    continue
                if value:
                    setattr(content, key, value)
            to_cache.append(content)

        return to_cache

    # Methods that return a SearchQuerySet.
    def all(self):
        """Returns all results for the query."""
        return self._clone()

    def search(self, **kwargs):
        clone = self._clone()
        clone.query = ElasticSearchQuery(**kwargs)
        return clone
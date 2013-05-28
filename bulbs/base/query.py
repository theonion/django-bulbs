import logging

from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from elasticutils import get_es
from elasticutils import S

REPR_OUTPUT_SIZE = 25
FETCH_LIMIT = 25


class ElasticSearchQuery(object):
    def __init__(self, published=True, content_type=None, tags=[]):
        self.size, self.start = 10, 0
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
        self.tags = None
        if tags:
            self.tags = {
                'nested': {
                    'path': 'tags',
                    'query': {
                        'bool': {
                            'must': [{
                                'term': {'tags.slug': [tag for tag in tags]}
                            }]
                        }
                    }
                }
            }

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

    def data(self, limit=None):
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
            },
        }
        if limit:
            search_data['from'] = limit.start
            if limit.stop:
                search_data['size'] = limit.stop - limit.start
        return search_data


class ElasticQuerySet(object):
    """
    Provides a way to specify search parameters and lazily load results.

    Supports chaining (a la QuerySet) to narrow the search.
    """
    def __init__(self, model, query=None):
        # ``_using`` should only ever be a value other than ``None`` if it's
        # been forced with the ``.using`` method.
        es = get_es(urls=settings.ES_URLS)

        if query is None:
            self.query = ElasticSearchQuery()
        else:
            self.query = query

        self.model = model

        self._result_cache = []
        self._result_count = None
        self._result_cache_index = 0

        self.log = logging.getLogger('elastic')

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE])

        if len(self) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."

        return repr(data)

    def __len__(self):
        if self._result_count is None:
            results = self._search(data=self.query.data(), params={'search_type': 'count'})
            self._result_count = results['hits']['total']
        return self._result_count

    def __iter__(self):
        for val in self._lazy_cache(slice(0, None)):
            yield val

    def _objectify(self, result):
        content = self.model()
        content.pk = result['_id']
        # TODO: make this a "shallow" object, including only the head variables, and disable the setting/getting of body varibles
        for key, value in result['_source'].items():
            if key == "content_type":
                app_label, model = value.split(".")
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                content.content_type = content_type
                continue
            if value:
                setattr(content, key, value)
        return content

    def _search(self, data=None, params={}):
        import pprint
        response = self._es.get('content/_search', data=data, params=params)
        pprint.pprint(data)
        pprint.pprint(response)
        return response

    def _lazy_cache(self, k):
        if len(self._result_cache) == 0:
            result = self._search(self.query.data(limit=k))
            hits = result['hits']['hits']
            self._result_cache_index = 0
            self._result_cache = [self._objectify(hit) for hit in hits]
        elif k.start < self._result_cache_index:
            fetch_limit = slice(k.start, self._result_cache_index)
            result = self._search(self.query.data(limit=fetch_limit))
            hits = result['hits']['hits']
            prefix_results = [self._objectify(hit) for hit in hits]
            self._result_cache = prefix_results.extend(self._result_cache)
            self._result_cache_index -= len(prefix_results)
        else:
            _result_cache_end = self._result_cache_index + len(self._result_cache)
            if k.stop is None and _result_cache_end < self.__len__():
                fetch_limit = slice(_result_cache_end, self.__len__)
                result = self._search(self.query.data(limit=fetch_limit))
                hits = result['hits']['hits']

                postfix_results = [self._objectify(hit) for hit in hits]
                self._result_cache = self._result_cache.extend(postfix_results)

        start = k.start - self._result_cache_index
        stop = None
        if k.stop:
            stop = k.stop - self._result_cache_index
        return self._result_cache[start:stop]

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

        if isinstance(k, slice):
            return self._lazy_cache(k)
        else:
            return self._lazy_cache(slice(k, k+1))[0]

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
        self._result_cache = []
        self._result_count = None
        self._result_cache_index = 0
        self.query = ElasticSearchQuery()
        return self

    def search(self, **kwargs):
        self._result_cache = []
        self._result_count = None
        self._result_cache_index = 0
        self.query = ElasticSearchQuery(**kwargs)
        return self

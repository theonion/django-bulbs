from django.conf import settings
from elasticsearch import S

class TagCache:

    _cache = {}  # Maybe too terrible?

    @classmethod
    def count(cls, slug):
        # Gets the count for a tag, hopefully form an in-memory cache.
        cnt = cls._cache.get(slug)
        if cnt is None:
            index = settings.ES_INDEXES.get('default')
            cnt = S().es(urls=settings.ES_URLS).indexes(index).query(**{"tags.slug": slug}).count()
            cls._cache[slug] = cnt
        return cnt
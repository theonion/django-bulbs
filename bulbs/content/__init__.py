class TagCache:

    _cache = {}  # Maybe too terrible?

    @classmethod
    def count(cls, slug):
        from .models import Tag
        # Gets the count for a tag, hopefully form an in-memory cache.
        cnt = cls._cache.get(slug)
        if cnt is None:
            cnt = Tag.search_objects.s().query(**{"tags.slug": slug}).count()
            cls._cache[slug] = cnt
        return cnt

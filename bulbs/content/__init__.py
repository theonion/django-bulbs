class TagCache(object):
    """
    in-memory cache
    """

    _cache = {}  # Maybe too terrible?

    @classmethod
    def count(cls, slug):
        """get the number of objects in the cache for a given slug

        :param slug: cache key
        :return: `int`
        """
        from .models import Content
        # Gets the count for a tag, hopefully form an in-memory cache.
        cnt = cls._cache.get(slug)
        if cnt is None:
            cnt = Content.search_objects.search(tags=[slug]).count()
            cls._cache[slug] = cnt
        return cnt

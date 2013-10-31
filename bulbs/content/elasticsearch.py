"""This module contains classes that help deal with ElasticSearch"""

from elasticutils import SearchResults, S

class ShallowFeatureType(object):

    def __init__(self, name, slug=None):
        self.name = name
        self.slug = slug

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ShallowTag(object):

    def __init__(self, data):
        self.id   = data.get('id')
        self.name = data.get('name')
        self.slug = data.get('slug')


class ShallowAuthor(object):

    def __init__(self, data):
        self.id = data.get('id')
        self.username = data.get('username')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')

class ShallowAuthorRelation(list):

    def __init__(self, items):
        for item in items:
            self.append(ShallowAuthor(item))

    def all(self):
        return self

class ShallowTagRelation(list):

    def __init__(self, items):
        for item in items:
            self.append(ShallowTag(item))

    def all(self):
        return self


class ShallowObject(object):

    def __init__(self, data):
        for key, item in data.items():
            if hasattr(self, key):
                continue
            if isinstance(item, dict):
                setattr(self, key, ShallowObject(item))
            elif isinstance(item, list):
                setattr(self, key, ShallowRelation(item))
            else:
                setattr(self, key, item)

class ShallowRelation(list):
    def __init__(self, items):
        for item in items:
            self.append(ShallowObject(item))

    def all(self):
        return self

class ShallowContentResult(ShallowObject):

    def __init__(self, _source):
        self.feature_type = ShallowFeatureType(_source.get('feature_type'), slug=_source.get('feature_type.slug'))
        super(ShallowContentResult, self).__init__(_source)


class ShallowContentSearchResults(SearchResults):

    def set_objects(self, results):
        self.objects = []
        for r in results:
            self.objects.append(ShallowContentResult(r['_source']))

    def __iter__(self):
        return self.objects.__iter__()


class ShallowContentS(S):

    def get_results_class(self):
        return ShallowContentSearchResults
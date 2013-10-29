"""This module contains class that help deal with ElasticSearch"""

class ShallowFeatureType(str):

    def __init__(self, name, slug):
        self = name
        self.slug = slug


class ShallowTag(object):

    def __init__(self, data):
        self.id   = data.get('id')
        self.name = data.get('name')
        self.slug = data.get('slug')


class ShallowAuthor(object):

    def __init__(self, data):
        self.username = data.get('username')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')


class ShallowRelation(object):

    def __init__(self, klass, data):
        for datum in data:
            self.append(klass(datum))

    def all(self):
        return self


class ShallowContentResult(object):

    def __init__(self, _source):
        self._source = _source
        self.id = _source.get('id')
        self.image = _source.get('image')
        self.title = _source.get('title')
        self.slug = _source.get('slug')
        self.feature_type = ShallowFeatureType(_source.get('feature_type'), _source.get('feature_type.slug'))
        self.description = _source.get('description')
        self.tags = ShallowRelation(ShallowTag, _source.get('tags'))
        self.tags = ShallowRelation(ShallowAuthor, _source.get('authors'))


class ShallowContentSearchResults(SearchResults):

    def set_objects(self, results):
        self.objects = [
            ShallowContentResult(_source) for r['_source'] in results
        ]

    def __iter__(self):
        return self.objects.__iter__()


class ShallowContentS(S):

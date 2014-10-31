"""
This module stores code for Shallow content results.

In the future, we should remove this, and pass
simple dictionaries into our templates.
"""

from datetime import datetime

from elasticutils import SearchResults
from django.utils import timezone
from django.utils.timezone import utc
import bulbs.content

from elastimorphic.base import PolymorphicS, ModelSearchResults


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
            if isinstance(item, dict):
                self.append(ShallowObject(item))
            else:
                self.append(item)

    def all(self):
        return self


class ShallowContentResult(ShallowObject):

    def __init__(self, _source, type=None):
        if type:
            self.type = type

        published_utc = None
        if _source.get('published'):
            try:
                published_utc = datetime.strptime(
                    _source.get('published'), '%Y-%m-%dT%H:%M:%S.%f+00:00'
                ).replace(tzinfo=utc)
            except ValueError:
                try:
                    published_utc = datetime.strptime(
                        _source.get('published'), '%Y-%m-%dT%H:%M:%S+00:00'
                    ).replace(tzinfo=utc)
                except ValueError:
                    pass

        if published_utc:
            self.published = timezone.localtime(published_utc)
        else:
            self.published = None

        self.feature_type = ShallowFeatureType(
            _source.get('feature_type').get('name'),
            slug=_source.get('feature_type').get('slug'))
        super(ShallowContentResult, self).__init__(_source)

    def __unicode__(self):
        return "<Content>"

    def __repr__(self):
        return "<Content>"

    def get_absolute_url(self):
        return getattr(self, 'absolute_url', None)

    @property
    def is_published(self):
        if self.published:
            now = timezone.now()
            if now >= self.published:
                return True
        return False

    def ordered_tags(self):
        tags = list(self.tags.all())
        sorted(tags, key=lambda tag: ((tag.type != "content_tag") * 100000) + bulbs.content.TagCache.count(tag.slug))
        return tags


class ShallowContentSearchResults(SearchResults):

    def set_objects(self, results):
        self.objects = []
        for r in results:
            self.objects.append(ShallowContentResult(r['_source'], type=r['_type']))

    def __iter__(self):
        return self.objects.__iter__()


class ShallowContentS(PolymorphicS):

    def get_results_class(self):
        if self.as_models:
            return ModelSearchResults
        return ShallowContentSearchResults

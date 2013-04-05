import rawes

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from bulbs.base.query import ElasticQuerySet


class ContentManager(models.Manager):

    def all(self):
        return ElasticQuerySet(Content).all()

    def search(self, **kwargs):
        """
        If ElasticSearch is being used, we'll use that for the query, and otherwise
        fall back to Django's .filter().

        Allowed params:

         * query
         * tag(s)?
         * content_type
         * published
        """

        return ElasticQuerySet(Content).search(**kwargs)


class Content(object):
    """
    Base Content object.

    This object includes all the "head" data.

    """
    objects = ContentManager()


class Tagish(models.Model):
    pass


class ContentBase(models.Model):
    """
    Abstract base class for objects that'd like to be considered 'content.'
    """

    # TODO: Add universal content ID?
    es_id = models.CharField(max_length=255, null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    subhead = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=510)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)  # This is an overridable field that is by default the author names
    _tags = models.TextField(null=True, blank=True)  # A comma-separated list of slugs, exposed as a list of strings
    _feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.

    class Meta:
        abstract = True

    def __unicode__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        return ""

    def save(self, *args, **kwargs):
        super(ContentBase, self).save(*args, **kwargs)
        self.update_index()

    def to_dict(self):
        content_type = ContentType.objects.get_for_model(self)
        data = {
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'byline': self.byline,
            'subhead': self.subhead,
            'published': self.published,
            'feature_type': self.feature_type,
            'tags': self.tags,
            'content_type': '%s.%s' % (content_type.app_label, content_type.model),
            'object_id': self.id
        }
        return data

    def update_index(self):
        es = rawes.Elastic(**settings.ES_SERVER)
        es_data = self.to_dict()

        if self.es_id:
            response = es.put('content/%s' % self.es_id, data=es_data)
        else:
            response = es.post('content/', data=es_data)
            self.es_id = response['_id']
            self.save()

    @property
    def tags(self):
        if self._tags:
            return [tag.strip().lower() for tag in self._tags.split(",")]
        return None

    @tags.setter
    def tags(self, value):
        # TODO: is this too terrible? Should a setter really have this behavior? Too implicit?
        if isinstance(value, basestring):
            self._tags = ",".join([tag.strip().lower() for tag in self._tags.split(",")])
        else:
            self._tags = ",".join([tag.strip().lower() for tag in value])

    @property
    def byline(self):
        # If the subclass has customized the byline accessing, use that.
        if hasattr(self, 'get_byline'):
            return self.get_byline()

        # If we have an override byline, we'll use that first.
        if self._byline:
            return self._byline

        # If we have authors, just put them in a list
        if self.authors.exists():
            return ", ".join([user.get_full_name() for user in self.authors.all()])

        # Well, shit. I guess there's no byline.
        return None

    @byline.setter
    def byline(self, value):
        self._byline = value

    @property
    def feature_type(self):
        # If the subclass has customized the feature_type accessing, use that.
        if hasattr(self, 'get_feature_type'):
            return self.get_feature_type()

        if self._feature_type:
            return self._feature_type

        return None

    @feature_type.setter
    def feature_type(self, value):
        self._feature_type = value

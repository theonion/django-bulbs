from django.conf import settings
from django.db import models
from polymorphic import PolymorphicModel


class Content(PolymorphicModel):
    """The base content model from which all content derives."""
    time_published = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.CharField(max_length=1024)

    _byline = models.CharField(max_length=255, null=True, blank=True)  # This is an overridable field that is by default the author names
    _tags = models.TextField(null=True, blank=True)  # A return-separated list of tag names, exposed as a list of strings
    _feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return self.title

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


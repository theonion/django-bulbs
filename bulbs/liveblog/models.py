from django.db import models

# from djes.models import Indexable

from bulbs.content.models import Content
from bulbs.liveblog.utils import (get_liveblog_author_model,
                                  get_liveblog_model)


class AbstractLiveBlog(models.Model):
    """Base mixin inherited by each property's concrete LiveBlog implementation (along with base
    content class).
    """

    recirc_content = models.ManyToManyField(Content, related_name='liveblog_recirc')

    class Meta:
        abstract = True


class LiveBlogEntry(models.Model):

    # Must import class (using string values for ForeignKeys doesn't work)
    liveblog = models.ForeignKey(get_liveblog_model(), related_name='entries')

    published = models.DateTimeField(blank=True, null=True)
    authors = models.ManyToManyField(get_liveblog_author_model())
    headline = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    recirc_content = models.ManyToManyField(Content, related_name='liveblog_entry_recirc')


class LiveBlogResponse(models.Model):

    entry = models.ForeignKey(LiveBlogEntry, related_name='responses')
    ordering = models.IntegerField(blank=True, null=True, default=None)

    author = models.ForeignKey(get_liveblog_author_model())
    body = models.TextField(blank=True)

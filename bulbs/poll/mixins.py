from django.db import models

from djbetty import ImageField

from bulbs.content.models import Content, ElasticsearchImageField

from .managers import PollManager


class PollMixin(models.Model):
    """Give a child object all Poll related fields and logic."""
    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")
    last_answer_index = models.IntegerField(default=0)
    end_date = models.DateTimeField(null=True, default=None)
    poll_image = ImageField(null=True, blank=True)
    answer_type = models.TextField(blank=True, default="text")

    search_objects = PollManager()

    class Meta:
        abstract = True

        # This keeps Poll out of Content.search_objects
    class Mapping(Content.Mapping):
        poll_image = ElasticsearchImageField()

        class Meta():
            orphaned = True


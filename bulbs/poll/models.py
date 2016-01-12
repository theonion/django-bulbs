from django.db import models
from bulbs.content.models import Content
from djes.models import Indexable
import requests

class Poll(Content):
    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")

    def sodahead_payload(self):
        return {
                'access_token': 'AQAAAHF5KS4FPOM0cmsxM5jrxDS9pmvPPtDI6M3qnbL8fX4ym5VGMUzH4sWBXxJnv-jNBw==',
                'name': self.title,
                'title': self.question_text
                }

    def save(self, *args, **kwargs):
        if self.sodahead_id is "":
            # post request
            response = requests.post('http://onion.sodahead.com/api/poll', self.sodahead_payload())
            self.sodahead_id = response.json()['polls'][0]['poll']['id']
        super(Poll, self).save(*args, **kwargs)

class Answer(Indexable):
    poll = models.ForeignKey(Poll,
        on_delete=models.CASCADE
    )


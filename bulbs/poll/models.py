from django.db import models

class Poll(models.Model):
    answer_text = models.TextField(blank=True, default="")

class Answer(models.Model):
    poll = models.ForeignKey(Poll,
        on_delete=models.CASCADE
    )

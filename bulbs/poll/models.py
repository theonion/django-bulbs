from django.db import models


class Poll(models.Model):
    question_text = models.TextField(blank=True, default="")

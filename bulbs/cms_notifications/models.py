from django.db import models


class CmsNotification(models.Model):
    """A CMS notification.
    """

    title = models.CharField(max_length=110)
    body = models.TextField(blank=True)
    post_date = models.DateTimeField()
    notify_end_date = models.DateTimeField()

    class Meta:
        ordering = ['-id']

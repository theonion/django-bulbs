from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from bulbs.content.models import Content

from .utils import update_content_contributions


@receiver(m2m_changed, sender=Content.authors.through)
def update_contributions(sender, instance, action, model, pk_set, **kwargs):
    """Creates a contribution for each author added to an article.
    """
    # action = kwargs.get('action')
    if action != 'pre_add':
        return
    else:
        # model = kwargs.get('model')
        # pk_set = kwargs.get('pk_set')
        for author in model.objects.filter(pk__in=pk_set):
            update_content_contributions(instance, author)

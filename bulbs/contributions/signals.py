from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from bulbs.content.models import Content

from .models import ReportContent, Contribution, ContributorRole
from .utils import update_content_contributions


@receiver(m2m_changed, sender=Content.authors.through)
def update_contributions(sender, instance, action, model, pk_set, **kwargs):
    """Creates a contribution for each author added to an article.
    """
    # action = kwargs.get('action')
    # import pdb; pdb.set_trace()
    if action != 'pre_add':
        return
    else:
        # model = kwargs.get('model')
        # pk_set = kwargs.get('pk_set')
        for author in model.objects.filter(pk__in=pk_set):
            update_content_contributions(instance, author)


@receiver(post_save, sender=Content)
def index_reportcontent(sender, instance, **kwargs):
    """
    Indexes the reporting document for the piece of content
    """
    try:
        proxy = ReportContent.reference.get(id=instance.id)
        proxy.index()
    except:
        pass


@receiver(post_save, sender=Contribution)
def index_relations(sender, instance, **kwargs):
    """
    We need to update the ReportContent object whenver a contribution is added.
    """
    try:
        proxy = ReportContent.reference.get(id=instance.content_id)
        proxy.index()
    except:
        pass


@receiver(post_save, sender=ContributorRole)
def update_rates(sender, instance, **kwargs):
    for contribution in instance.contribution_set.all():
        contribution.save()


# @receiver(post_save, sender=ContributionOverride)
# def update_contribution_from_override(sender, instance, **kwargs):


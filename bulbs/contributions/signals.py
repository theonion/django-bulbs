from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from bulbs.content.models import Content, FeatureType

from .models import Contribution, ContributorRole, FeatureTypeRate, ReportContent
from .tasks import update_role_rates
from .utils import update_content_contributions


@receiver(post_save, sender=FeatureType)
def update_feature_type_rates(sender, instance, created, *args, **kwargs):
    """
    Creates a default FeatureTypeRate for each role after the creation of a FeatureTypeRate.
    """
    if created:
        for role in ContributorRole.objects.all():
            FeatureTypeRate.objects.create(role=role, feature_type=instance, rate=0)


@receiver(post_save, sender=ContributorRole)
def call_update_role_rates(sender, instance, * args, **kwargs):
    update_role_rates.delay(instance.pk)


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

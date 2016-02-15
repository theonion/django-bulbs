from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from bulbs.content.models import Content, FeatureType

from .models import ContributorRole, FeatureTypeRate
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
    if action != 'pre_add':
        return
    else:
        for author in model.objects.filter(pk__in=pk_set):
            update_content_contributions(instance, author)

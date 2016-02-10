from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from bulbs.content.models import Content, FeatureType

from .models import Contribution, ContributorRole, FeatureTypeRate, ReportContent
from .tasks import update_contribution_index_from_content, update_role_rates
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


@receiver(post_save, sender=Contribution)
def index_relations(sender, instance, **kwargs):
    """
    We need to update the ReportContent object whenver a contribution is added.
    """
    try:
        proxy = ReportContent.reference.get(id=instance.content_id)
        proxy.index()
    except ObjectDoesNotExist:
        pass


def index_content_dependencies(sender, instance, **kwargs):
    """
    Indexes the reporting document for the piece of content
    """
    update_contribution_index_from_content.delay(instance.id)
    try:
        proxy = ReportContent.reference.get(id=instance.id)
        proxy.index()
    except ObjectDoesNotExist:
        pass

def get_all_cls_child_classes(cls, exclude=[]):
    clsses = [cls]
    for sub_cls in cls.__subclasses__():
        clsses += get_all_cls_child_classes(sub_cls)
    for exc_cls in exclude:
        try:
            index = clsses.index(exc_cls)
            clsses.pop(index)
        except:
            pass
    return clsses


# Signals are not aware of child classes, which creates a problem for indexing.
# This allows us to create a signal for each subclass of Content per property.
content_classes = get_all_cls_child_classes(Content, exclude=[ReportContent])
for content_class in content_classes:
    post_save.connect(
        index_content_dependencies,
        sender=content_class,
        dispatch_uid="att_post_save_" + content_class.__name__
    )

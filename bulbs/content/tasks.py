from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task


@shared_task(default_retry_delay=5)
def index(content_type_id, pk, refresh=False):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.model_class().objects.get(id=pk)
    obj.index(refresh=refresh)


@shared_task(default_retry_delay=5)
def index_content_contributions(content_pk):
    from bulbs.contributions.models import Contribution
    for contribution in Contribution.objects.filter(content__pk=content_pk):
        contribution.save()


@shared_task(default_retry_delay=5)
def index_content_report_content_proxy(content_pk):
    from bulbs.contributions.models import ReportContent
    try:
        proxy = ReportContent.reference.get(id=content_pk)
        proxy.index()
    except ObjectDoesNotExist:
        pass


@shared_task(default_retry_delay=5)
def index_feature_type_content(featuretype_pk):
    from .models import FeatureType
    featuretype = FeatureType.objects.get(pk=featuretype_pk)
    for content in featuretype.content_set.all():
        content.index()


@shared_task(default_retry_delay=5)
def update_feature_type_rates(featuretype_pk):
    from bulbs.contributions.models import ContributorRole, FeatureTypeRate, FEATURETYPE

    roles = ContributorRole.objects.filter(payment_type=FEATURETYPE)

    for role in roles:
        existing_rates = FeatureTypeRate.objects.filter(
            feature_type_id=featuretype_pk,
            role_id=role.pk)

        if existing_rates.count() == 0:
            FeatureTypeRate.objects.create(
                rate=0,
                feature_type_id=featuretype_pk,
                role_id=role.pk)


@shared_task(default_retry_delay=5)
def post_to_instant_articles_api(content_pk):
    import requests
    import logging

    from django.conf import settings
    from django.template.loader import render_to_string
    from django.template.base import TemplateDoesNotExist

    from bulbs.utils import vault
    from bulbs.instant_articles.renderer import InstantArticleRenderer
    from bulbs.instant_articles.transform import transform
    from .models import Content

    if getattr(settings, 'FACEBOOK_API_ENV', '').lower() == 'production':
        logger = logging.getLogger(__name__)

        content = Content.objects.get(pk=content_pk)
        feature_type = getattr(content, 'feature_type', None)

        fb_page_id = getattr(settings, 'FACEBOOK_PAGE_ID', '')
        fb_api_url = getattr(settings, 'FACEBOOK_API_BASE_URL', '')

        fb_access_token = vault.read(settings.FACEBOOK_TOKEN_VAULT_PATH)

        if feature_type and feature_type.instant_article and content.is_published:
            context = {
                "content": content,
                "absolute_uri": getattr(settings, 'WWW_URL'),
                "transformed_body": transform(
                    getattr(content, 'body', ""),
                    InstantArticleRenderer())
            }
            try:
                source = render_to_string(
                    "instant_article/_instant_article.html", context
                )
            except TemplateDoesNotExist:
                source = render_to_string(
                    "instant_article/base_instant_article.html", context
                )

            # Post article to instant article API
            post = requests.post(
                '{0}/{1}/instant_articles'.format(fb_api_url, fb_page_id),
                data={
                    'access_token': fb_access_token,
                    'html_source': source,
                    'published': 'true',
                    'development_mode': 'false'
                })

            # Get status of article
            status = requests.get('{0}/{1}?access_token={2}'.format(
                fb_api_url,
                post.json()['id'],
                fb_access_token
            ))

            # If upload if successful, set ia_id to id
            if status.json()['status'] == 'SUCCESS':
                # using a queryset.update() will stop save() from recursing
                Content.objects.filter(pk=content_pk).update(instant_article_id=status.json()['id'])
            else:
                logger.error('Error in posting to Instant Article API: {}'.format(
                    status.json()
                ))
        # if article is being unpublished, delete it from IA API
        elif (not content.is_published and
              content.instant_article_id):
            delete = requests.delete('{0}/{1}?access_token={2}'.format(
                fb_api_url,
                content.instant_article_id,
                fb_access_token
            ))

            status = delete.json()["success"]
            if bool(status) is not True:
                logger.error('''
                    Error in deleting Instant Article.\n
                    Content ID: {0}\n
                    IA ID: {1}\n
                    Error: {2}'''.format(
                        content.id,
                        content.instant_article_id,
                        delete.json()))

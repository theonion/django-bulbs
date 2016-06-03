import time

from django.conf import settings
from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

from bulbs.utils import vault
from bulbs.instant_articles.renderer import InstantArticleRenderer
from bulbs.instant_articles.transform import transform

import requests
import logging
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


def post_article(content, body):
    from .models import Content

    logger = logging.getLogger(__name__)
    fb_page_id = getattr(settings, 'FACEBOOK_PAGE_ID', '')
    fb_api_url = getattr(settings, 'FACEBOOK_API_BASE_URL', '')
    fb_access_token = vault.read(settings.FACEBOOK_TOKEN_VAULT_PATH)

    # Post article to instant article API
    post = requests.post(
        '{0}/{1}/instant_articles'.format(fb_api_url, fb_page_id),
        data={
            'access_token': fb_access_token,
            'html_source': body,
            'published': 'true',
            'development_mode': 'false'
        })

    if not post.ok:
        logger.error('''
            Error in posting Instant Article.\n
            Content ID: {0}\n
            IA ID: {1}\n
            Status Code: {2}'''.format(
                content.id,
                content.instant_article_id,
                post.status_code))
        return

    # Poll for status of article
    response = ""
    while response != "SUCCESS":
        time.sleep(1)

        status = requests.get('{0}/{1}?access_token={2}'.format(
            fb_api_url,
            post.json().get('id'),
            fb_access_token
        ))

        # log errors
        if not status.ok or status.json().get('status') == "ERROR":
            logger.error('''
                Error in getting status of Instant Article.\n
                Content ID: {0}\n
                IA ID: {1}\n
                Status Code: {2}'''.format(
                    content.id,
                    content.instant_article_id,
                    status.status_code))
            return

        response = status.json().get('status')

    # set instant_article_id to response id
    Content.objects.filter(pk=content.id).update(
        instant_article_id=status.json().get('id'))


def delete_article(content):
    logger = logging.getLogger(__name__)
    fb_api_url = getattr(settings, 'FACEBOOK_API_BASE_URL', '')
    fb_access_token = vault.read(settings.FACEBOOK_TOKEN_VAULT_PATH)

    delete = requests.delete('{0}/{1}?access_token={2}'.format(
        fb_api_url,
        content.instant_article_id,
        fb_access_token
    ))

    if not delete.ok:
        logger.error('''
            Error in deleting Instant Article.\n
            Content ID: {0}\n
            IA ID: {1}\n
            Status Code: {2}'''.format(
                content.id,
                content.instant_article_id,
                delete.status_code))
    else:
        status = delete.json().get('success')
        if bool(status) is not True:
            logger.error('''
                Error in deleting Instant Article.\n
                Content ID: {0}\n
                IA ID: {1}\n
                Error: {2}'''.format(
                    content.id,
                    content.instant_article_id,
                    delete.json()))


@shared_task(default_retry_delay=5, time_limit=300)
def post_to_instant_articles_api(content_pk):
    from .models import Content

    if getattr(settings, 'FACEBOOK_API_ENV', '').lower() == 'production':
        content = Content.objects.get(pk=content_pk)
        feature_type = getattr(content, 'feature_type', None)

        # if feature type is IA approved & content is published
        if feature_type and feature_type.instant_article and content.is_published:
            # render page source
            context = {
                'content': content,
                'absolute_uri': getattr(settings, 'WWW_URL'),
                'transformed_body': transform(
                    getattr(content, 'body', ''),
                    InstantArticleRenderer())
            }
            try:
                source = render_to_string(
                    'instant_article/_instant_article.html', context
                )
            except TemplateDoesNotExist:
                source = render_to_string(
                    'instant_article/base_instant_article.html', context
                )

            post_article(content, source)

        # if article is being unpublished, delete it from IA API
        elif (not content.is_published and
              content.instant_article_id):
            delete_article(content)

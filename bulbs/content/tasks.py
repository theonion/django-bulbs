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

logger = logging.getLogger(__name__)


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


def post_article(content, body, fb_page_id, fb_api_url, fb_token_path, fb_dev_mode, fb_publish):
    from .models import Content

    fb_access_token = vault.read(fb_token_path).get('authtoken')
    if fb_access_token is None:
        logger.error('Missing FB Auth Token in Vault.\n')
        return

    # Post article to instant article API
    post = requests.post(
        '{0}/{1}/instant_articles'.format(fb_api_url, fb_page_id),
        data={
            'access_token': fb_access_token,
            'html_source': body,
            'published': fb_publish,
            'development_mode': fb_dev_mode
        })

    if not post.ok:
        logger.error('''
                     Error in posting Instant Article.\n
                     Content ID: {0}\n
                     IA ID: {1}\n
                     Status Code: {2}
                     Request: {3}'''.format(content.id,
                                            content.instant_article_id,
                                            post.status_code,
                                            post.__dict__))
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
                Status Code: {2}
                Request: {3}'''.format(content.id,
                                       content.instant_article_id,
                                       status.status_code,
                                       status.__dict__))
            return

        response = status.json().get('status')

    # build URL
    base = getattr(settings, 'WWW_URL')
    if not base.startswith("http"):
        base = "http://" + base

    canonical_url = "{0}{1}".format(base, content.get_absolute_url())
    canon = requests.get('{0}?id={1}&fields=instant_article&access_token={2}'.format(
        fb_api_url,
        canonical_url,
        fb_access_token))

    if not canon.ok:
        logger.error('''
            Error in getting article ID of Instant Article.\n
            Content ID: {0}\n
            Status Code: {1}
            Request: {2}'''.format(content.id,
                                   canon.status_code,
                                   canon.__dict__))
        return

    # set instant_article_id to response id
    Content.objects.filter(pk=content.id).update(
        instant_article_id=canon.json().get('instant_article').get('id'))


def delete_article(content, fb_api_url, fb_token_path):
    fb_access_token = vault.read(fb_token_path).get('authtoken')
    if fb_access_token is None:
        logger.error('Missing FB Auth Token in Vault.\n')
        return

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
                     Status Code: {2}
                     Request: {3}'''.format(content.id,
                                            content.instant_article_id,
                                            delete.status_code,
                                            delete.__dict__))
    else:
        status = delete.json().get('success')
        if bool(status) is not True:
            logger.error('''
                Error in deleting Instant Article.\n
                Content ID: {0}\n
                IA ID: {1}\n
                Error: {2}'''.format(content.id,
                                     content.instant_article_id,
                                     delete.json()))


@shared_task(default_retry_delay=5, time_limit=300)
def post_to_instant_articles_api(content_pk):
    from .models import Content
    content = Content.objects.get(pk=content_pk)

    fb_page_id = getattr(settings, 'FACEBOOK_PAGE_ID', None)
    fb_api_url = getattr(settings, 'FACEBOOK_API_BASE_URL', None)
    fb_token_path = getattr(settings, 'FACEBOOK_TOKEN_VAULT_PATH', None)
    fb_dev_mode = 'true' if getattr(settings, 'FACEBOOK_API_DEVELOPMENT_MODE', False) else 'false'
    fb_publish = 'true' if getattr(settings, 'FACEBOOK_API_PUBLISH_ARTICLE', False) else 'false'
    should_post = getattr(settings, 'FACEBOOK_POST_TO_IA', False)

    if not fb_page_id or not fb_api_url or not fb_token_path:
        logger.error('''
                     Error in Django Settings.\n
                     FACEBOOK_PAGE_ID: {0}\n
                     FACEBOOK_API_BASE_URL: {1}\n
                     FACEBOOK_TOKEN_VAULT_PATH: {2}'''.format(fb_page_id,
                                                              fb_api_url,
                                                              fb_token_path))
        return

    # if feature type is IA approved & content is published
    feature_type = getattr(content, 'feature_type', None)
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

        if should_post:
            post_article(
                content,
                source,
                fb_page_id,
                fb_api_url,
                fb_token_path,
                fb_dev_mode,
                fb_publish)

    # if article is being unpublished, delete it from IA API
    elif not content.is_published and content.instant_article_id:
        if should_post:
            delete_article(
                content,
                fb_api_url,
                fb_token_path)

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
    from django.conf import settings
    from .models import Content

    content = Content.objects.get(pk=content_pk)
    if content.feature_type.instant_article:
        # GET FACEBOOK_PAGE_ID FROM SETTINGS
        fb_page_id = getattr(settings, 'FACEBOOK_PAGE_ID')
        # GET ACCESS TOKEN FROM VAULT
        fb_access_token = ""

        # GET PAGE SOURCE FROM INSTANT ARTICLE CONTENT VIEW
        source = ""

        # POST IT TO FACEBOOK ENDPOINT
        # curl \
        #     -F 'access_token={access-token}' \
        #     -F 'html_source=<!doctype html>...' \
        #     -F 'published=true' \
        #     -F 'development_mode=false' \
        #     https://graph.facebook.com/{page-id}/instant_articles
        post = requests.post(
            'https://graph.facebook.com/{}/instant_articles'.format(fb_page_id),
            data={
                'access_token': fb_access_token,
                'html_source': source,
                'published': 'true',
                'development_mode': 'false'
            })

        # GET IMPORT STATUS ID FROM RESPONSE
        # GET https://graph.facebook.com/{import-status-id}?access_token={access-token}
        status = requests.get('https://graph.facebook.com/{0}?access_token={1}'.format(
            post.json()['id'],
            fb_access_token
        ))

        # CHECK STATUS IN RESPONSE
        if status.json()['status'] == 'SUCCESS':
            content.instant_article_id = status.json()['id']
            content.save()
        else:
            pass
            # log error here

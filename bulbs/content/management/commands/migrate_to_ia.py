import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist

from bulbs.content.models import Content, FeatureType
from bulbs.instant_articles.renderer import InstantArticleRenderer
from bulbs.instant_articles.transform import transform
from bulbs.utils import vault

import requests
import timezone


class Command(BaseCommand):

    fb_page_id = getattr(settings, 'FACEBOOK_PAGE_ID', None)
    fb_api_url = getattr(settings, 'FACEBOOK_API_BASE_URL', None)
    fb_dev_mode = 'true' if getattr(settings, 'FACEBOOK_API_DEVELOPMENT_MODE', False) else 'false'
    fb_publish = 'true' if getattr(settings, 'FACEBOOK_API_PUBLISH_ARTICLE', False) else 'false'
    should_post = getattr(settings, 'FACEBOOK_POST_TO_IA', False)
    fb_access_token = vault.read(getattr(settings, 'FACEBOOK_TOKEN_VAULT_PATH', None)).get('authtoken')
    www_url = getattr(settings, 'WWW_URL', None)

    def add_arguments(self, parser):
        parser.add_argument('feature', nargs="+", type=str)

    def generate_body(self, content):
        context = {
            'content': content,
            'absolute_uri': self.www_url,
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

            return source

    def post_content(self, content):
        body = self.generate_body(content)

        # Post article to instant article API
        post = requests.post(
            '{0}/{1}/instant_articles'.format(self.fb_api_url, self.fb_page_id),
            data={
                'access_token': self.fb_access_token,
                'html_source': body,
                'published': self.fb_publish,
                'development_mode': self.fb_dev_mode
            })

        if not post.ok:
            print('''
                Error in posting Instant Article.\n
                Content ID: {0}\n
                IA ID: {1}\n
                Status Code: {2}
                Request: {3}'''.format(
                    content.id,
                    content.instant_article_id,
                    post.status_code,
                    post.__dict__))
            raise CommandError('Breaking command.')

        # Poll for status of article
        response = ""
        while response != "SUCCESS":
            time.sleep(1)

            status = requests.get('{0}/{1}?access_token={2}'.format(
                self.fb_api_url,
                post.json().get('id'),
                self.fb_access_token
            ))

            # log errors
            if not status.ok or status.json().get('status') == "ERROR":
                print('''
                    Error in getting status of Instant Article.\n
                    Content ID: {0}\n
                    IA ID: {1}\n
                    Status Code: {2}
                    Request: {3}'''.format(
                        content.id,
                        content.instant_article_id,
                        status.status_code,
                        status.__dict__))
                raise CommandError('Breaking command.')

            response = status.json().get('status')

        # set instant_article_id to response id
        Content.objects.filter(pk=content.id).update(
            instant_article_id=status.json().get('id'))

    def handle(self, *args, **options):
        if (not self.fb_page_id or
            not self.fb_api_url or
            not self.fb_access_token or
            not self.www_url):
            print('''
                Error in Django Settings.\n
                FACEBOOK_PAGE_ID: {0}\n
                FACEBOOK_API_BASE_URL: {1}\n
                ACCESS TOKEN: {2}
                WWW_URL: {3}'''.format(
                    self.fb_page_id,
                    self.fb_api_url,
                    self.fb_access_token,
                    self.www_url))
            raise CommandError('Breaking command.')

        if not self.should_post:
            print('FACEBOOK_POST_TO_IA set to False')
            raise CommandError('Breaking command.')

        feature_types = FeatureType.objects.all()

        feature = options['feature'][0]
        if feature:
            feature_types.objects.filter(slug=feature)

        for ft in feature_types:
            if ft.instant_article:

                # All published content belonging to feature type
                c = Content.objects.filter(
                    feature_type=ft,
                    published__isnull=False,
                    published__lte=timezone.now())

                if not c.instant_article_id:
                    self.post_content(c)

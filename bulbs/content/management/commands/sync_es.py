from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from django.db import models

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError

from bulbs.content.models import Content, Tag


class Command(NoArgsCommand):
    args = ''
    help = 'Create the Elastic Search indexes and mappings tables for all apps in INSTALLED_APPS.'

    def handle(self, **options):
        self.style = no_style()

        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        try:
            es.create_index(index)
        except IndexAlreadyExistsError:
            pass

        for mapping_name, model in Content.get_doctypes().items():
            es.put_mapping(
                index,
                mapping_name,
                model.get_mapping()
            )

        tag_mapping = Tag.get_mapping()
        es.put_mapping(index, 'tag', tag_mapping)

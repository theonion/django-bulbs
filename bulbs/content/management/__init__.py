from django.db.models.signals import post_syncdb
from django.conf import settings

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError

import bulbs.content.models


def sync_es(sender, **kwargs):
    # Your specific logic here
    es = get_es(urls=settings.ES_URLS)
    index = settings.ES_INDEXES.get('default')
    try:
        es.create_index(index)
    except IndexAlreadyExistsError:
        pass

    for mapping_name, model in bulbs.content.models.Content.get_doctypes().items():
        es.put_mapping(
            index,
            mapping_name,
            model.get_mapping()
        )

    tag_mapping = bulbs.content.models.Tag.get_mapping()
    es.put_mapping(index, 'tag', tag_mapping)


post_syncdb.connect(sync_es, sender=bulbs.content.models)

from django.db.models.signals import post_syncdb
from django.conf import settings

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

import bulbs.content.models


def sync_es(sender, **kwargs):
    # Your specific logic here
    es = get_es(urls=settings.ES_URLS)
    index = settings.ES_INDEXES.get('default')

    mappings = {}
    for name, model in bulbs.content.models.Content.get_doctypes().items():
        mappings[name] = model.get_mapping()

    for name, model in bulbs.content.models.Tag.get_doctypes().items():
        mappings[name] = model.get_mapping()

    # analysis = {
    #     "analyzer": {
        
    #     }
    # }

    try:
        es.create_index(index, settings= {
            "mappings": mappings,
        })
    except IndexAlreadyExistsError:
        pass
    except ElasticHttpError as e:
        print("ES Error: %s" % e.error)


post_syncdb.connect(sync_es, sender=bulbs.content.models)

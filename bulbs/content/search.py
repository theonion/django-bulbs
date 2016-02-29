from elasticsearch_dsl import function, query


def randomize_es(es_queryset):
    """Randomize an elasticsearch queryset."""
    return es_queryset.query(
        query.FunctionScore(
            functions=[function.RandomScore()]
        )
    ).sort("-_score")

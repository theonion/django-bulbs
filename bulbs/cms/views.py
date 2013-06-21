import json

from django.http import HttpResponse
from django.conf import settings

from elasticutils import S

from bulbs.content.views import ContentListView
from bulbs.content.models import Contentish


class AdminListView(ContentListView):

    template_name = "cms/list.html"

    def get_context_data(self, **kwargs):
        context = super(AdminListView, self).get_context_data(**kwargs)

        results = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES.get('default'))
        facet_counts = results.facet_raw(feature_type={'terms': {'field': 'feature_type.slug', 'size': 20}}).facet_counts()
        slug_facets = facet_counts['feature_type'][::2]
        names_facets = facet_counts['feature_type'][1::2]
        feature_data = [{
            'slug': facet['term'],
            'count': facet['count']
        } for facet in slug_facets]
        for index, facet in enumerate(names_facets):
            feature_data[index]['name'] = facet['term']

        context['features'] = feature_data
        context['doctypes'] = {}
        for mapping_name, contentish in Contentish.get_doctypes().items():
            context['doctypes'][mapping_name] = contentish.__name__

        return context

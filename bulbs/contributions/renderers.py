from collections import OrderedDict
import csv

from rest_framework_csv.renderers import CSVRenderer
from rest_framework_csv.misc import Echo
import six

import django.db.models.query

from djes.utils.query import batched_queryset


# DJES LazySearch iteration is a hot mess, and by default will only iterate through a full page (10
# items). This works for now, but eventually we need to just fix DJES
class LazySearchIterator(object):

    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return next(self.queryset)


class CSVStreamingRenderer(CSVRenderer):
    """
        Renders serialized *data* into CSV to be used with Django
        StreamingHttpResponse. We need to return a generator here, so Django
        can iterate over it, rendering and returning each line.

        Based on rest_framework_csv.renderers.CSVStreamingRenderer, but can't use that b/c the
        `tabilize()` call is not iterator-friendly.
    """

    header_fields = {}

    def render(self, data, media_type=None, renderer_context={}):

        queryset = data['queryset']
        serializer = data['serializer']
        context = data['context']

        csv_buffer = Echo()
        csv_writer = csv.writer(csv_buffer)

        # Header row
        if queryset.count():
            yield csv_writer.writerow(self.header_fields.values())

        # Need to efficiently page through querysets
        if isinstance(queryset, django.db.models.query.QuerySet):
            queryset = batched_queryset(queryset, chunksize=25)
        else:
            # This should be build into LazySearch object, but it's not...
            queryset = LazySearchIterator(queryset)

        # Data rows
        for item in queryset:
            items = serializer(item, context=context).data
            # Sort by `header_fields` ordering
            ordered = [items[column] for column in self.header_fields]
            yield csv_writer.writerow([
                elem.encode('utf-8') if isinstance(elem, six.text_type) and six.PY2 else elem
                for elem in ordered
            ])


class ContentReportingRenderer(CSVStreamingRenderer):

    header_fields = OrderedDict([
        ('published', 'Publish Date'),
        ('id', 'Content ID'),
        ('title', 'Title'),
        ('feature_type', 'Feature Type'),
        ('url', 'URL'),
        ('content_type', 'Content Type'),
        ('authors', 'Authors'),
        ('video_id', 'Video ID'),
        ('value', 'Value'),
    ])


class ContributionReportingRenderer(CSVStreamingRenderer):

    header_fields = OrderedDict([
        ('publish_date', 'Publish Date'),
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('id', 'Content ID'),
        ('title', 'Title'),
        ('feature_type', 'Feature Type'),
        ('rate', 'Rate'),
        ('payroll_name', 'Payroll Name'),
    ])


class FreelanceProfileRenderer(CSVStreamingRenderer):

    header_fields = OrderedDict([
        ('contributor', 'Contributor'),
        ('payment_date', 'Payment Date'),
        ('pay', 'Pay'),
        ('contributions_count', 'Contributions Count'),
    ])


class LineItemRenderer(CSVStreamingRenderer):

    header_fields = OrderedDict([
        ('payment_date', 'Payment Date'),
        ('payroll_name', 'Payroll Name'),
        ('amount', 'Amount'),
        ('note', 'Note'),
    ])

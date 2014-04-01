import dateutil.parser
from rest_framework import filters


class DoctypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        doctypes = request.REQUEST.getlist("doctype")
        if doctypes:
            classes = []
            for doctype in doctypes:
                klass = view.model._cache[doctype]
                classes.append(klass)
            queryset = queryset.instance_of(*classes)
        return queryset


class TagSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_tags = request.REQUEST.getlist("tags")
        if search_tags:
            queryset = queryset.filter(tags__in=search_tags)
        return queryset


class AuthorSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_authors = request.REQUEST.getlist("authors")
        if search_authors:
            queryset = queryset.filter(authors__in=search_authors)
        return queryset


class DateSearchFilter(filters.BaseFilterBackend):
    start_date_field = "start_date"
    end_date_field = "end_date"
    filter_field = "published"

    def filter_queryset(self, request, queryset, view):
        start_date = request.REQUEST.get(self.start_date_field, None)
        end_date = request.REQUEST.get(self.end_date_field, None)
        if not (start_date or end_date):
            return queryset

        filter_kwargs = {}
        if start_date and end_date:
            start_date = dateutil.parser.parse(start_date)
            end_date = dateutil.parser.parse(end_date)
            filter_kwargs = {
                self.filter_field + "__range": (start_date, end_date)
            }
        else:
            filter_date = dateutil.parser.parse(start_date or end_date)
            filter_kwargs[self.filter_field] = filter_date

        return queryset.filter(**filter_kwargs)

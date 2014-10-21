from django.conf.urls import patterns, url, include

from bulbs.content.views import ContentListView
from tests.testcontent.views import TestContentDetailView


urlpatterns = patterns("",
    url(r"^api/v1/", include("bulbs.api.urls")),  # noqa
    url(r"^content_list_one\.html",
        ContentListView.as_view(template_name="testapp/content_list.html")),

    # testing unpublished links
    url(r"^unpublished/(?P<token>\w+)$", TestContentDetailView.as_view(), name="unpublished"),
    url(r"^detail/(?P<pk>\d+)/$", "tests.testcontent.views.test_content_detail", name="published"),

    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)

from django.conf.urls import patterns, url, include

from bulbs.content.views import ContentListView

urlpatterns = patterns("",
    url(r"^api/v1/", include("bulbs.api.urls")),  # noqa
    url(r"^content_list_one\.html", "tests.testcontent.views.test_all_content_list"),
    url(r"^content_list_two\.html", "tests.testcontent.views.test_content_two_list"),
    url(r"^published_custom_search/$", "tests.testcontent.views.test_published_content_custom_search_list"),
    url(r"^unpublished_custom_search/$", "tests.testcontent.views.test_unpublished_content_custom_search_list"),
    # testing unpublished links
    url(r"^unpublished/(?P<token>\w+)$", "bulbs.content.views.unpublished", name="unpublished"),
    url(r"^detail/(?P<pk>\d+)/$", "tests.testcontent.views.test_content_detail", name="published"),

    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)

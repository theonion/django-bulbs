from django.conf.urls import patterns, url, include

urlpatterns = patterns("",
    url(r"^", include("bulbs.api.urls")),  # noqa
    url(r"^", include("bulbs.poll.urls")), # noqa
    url(r"^content_list_one\.html", "example.testcontent.views.test_all_content_list"),
    url(r"^content_list_two\.html", "example.testcontent.views.test_content_two_list"),
    url(r"^published_custom_search/$", "example.testcontent.views.test_published_content_custom_search_list"),
    url(r"^unpublished_custom_search/$", "example.testcontent.views.test_unpublished_content_custom_search_list"),
    # testing unpublished links
    url(r"^unpublished/(?P<token>\w+)$", "bulbs.content.views.unpublished", name="unpublished"),
    url(r"^detail/(?P<pk>\d+)/$", "example.testcontent.views.test_content_detail", name="published"),

    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)

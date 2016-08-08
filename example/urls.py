from django.conf.urls import patterns, url, include

urlpatterns = patterns("",
    url(r"^api/v1/", include("bulbs.api.urls")),  # noqa
    url(r"^", include("bulbs.ads.urls")),
    url(r"^", include("bulbs.poll.urls")),  # noqa
    url(r"^(?P<pk>\d+)/recirc", "bulbs.recirc.views.recirc", name="content_recirc"),
    url(r"^(?P<pk>\d+)/inline-recirc", "bulbs.recirc.views.inline_recirc", name="content_inline_recirc"),
    url(r"^content_list_one\.html", "example.testcontent.views.test_all_content_list"),
    url(r"^content_list_two\.html", "example.testcontent.views.test_content_two_list"),
    url(r"^published_custom_search/$", "example.testcontent.views.test_published_content_custom_search_list"),
    url(r"^unpublished_custom_search/$", "example.testcontent.views.test_unpublished_content_custom_search_list"),
    # testing unpublished links
    url(r"^unpublished/(?P<token>\w+)$", "bulbs.content.views.unpublished", name="unpublished"),
    url(r"^detail/(?P<pk>\d+)/$", "example.testcontent.views.test_content_detail", name="published"),
    url(r"^special/(?P<slug>[\w-]+)/?$", "bulbs.special_coverage.views.special_coverage", name="special"),
    url(r"", include("bulbs.instant_articles.urls")),
    url(r"", include("bulbs.videos.urls")),
    url(r"", include("bulbs.notifications.urls")),

    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)

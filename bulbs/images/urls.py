from django.conf.urls import url, patterns

urlpatterns = patterns('bulbs.images.views',
    url(r'^crops/(?P<image_id>\d+)/(?P<ratio>[a-z0-9-]+)/(?P<width>\d{1,4})_(?P<quality>\d{1,3}).(?P<extension>jpg|png|gif)$', 'crop_for_ratio', name="crop_for_ratio"),
    url(r'^crop/(?P<image_id>\d+)/$', 'crop_ratios', name='crop_ratios'),
)

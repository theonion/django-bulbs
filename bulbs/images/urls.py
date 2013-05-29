from django.conf.urls.defaults import *

urlpatterns = patterns(
    'bulbs.images.views',
    ('^[0-9]+/(?P<image_id>\d+)/(?P<ratio_slug>[a-z0-9-]+)/(?P<width>\d{1,4})(_(?P<quality>\d{1,2}))?.jpg$', 'crop_for_ratio'),
    ('^crop/(?P<image_id>\d+)/$', 'crop_ratios'),
)

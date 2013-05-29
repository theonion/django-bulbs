from django.conf.urls.defaults import *

urlpatterns = patterns('bulbs.images.views',
    ('^crops/(?P<image_id>\d+)/(?P<ratio>[a-z0-9-]+)/(?P<width>\d{1,4})_(?P<quality>\d{1,2}).(?P<extension>jpg|png|gif)$', 'crop_for_ratio'),
    ('^crop/(?P<image_id>\d+)/$', 'crop_ratios'),
)

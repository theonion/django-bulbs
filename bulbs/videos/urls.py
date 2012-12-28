from django.conf.urls import patterns

urlpatterns = patterns('bulbs.videos.views',
    (r'^aws_attrs\.js', 'aws_attrs'),
    (r'^upload_successful$', 'upload_successful')
)

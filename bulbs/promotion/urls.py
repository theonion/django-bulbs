from django.conf.urls import url, include

from .api import api_v1_router
from .views import OperationsViewSet

urlpatterns = (
    url(
        r"^pzone/(?P<pzone_pk>\d+)/operations/$",
        OperationsViewSet.as_view(),
        name="pzone_operations"
    ),
    url(
        r"^pzone/(?P<pzone_pk>\d+)/operations/(?P<operation_pk>\d+)/$",
        OperationsViewSet.as_view(),
        name="pzone_operations_delete"
    ),
    url(r"^", include(api_v1_router.urls)),       # noqa
)

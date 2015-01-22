from rest_framework import routers

from .views import PZoneViewSet


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"pzone", PZoneViewSet, base_name="pzone")

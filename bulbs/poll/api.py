from rest_framework.routers import DefaultRouter

from .viewsets import PollViewSet, AnswerViewSet

router = DefaultRouter(trailing_slash=True)

api_v1_router = DefaultRouter()
api_v1_router.register(
    r"poll",
    PollViewSet,
    base_name="poll")

api_v1_router.register(
    r"poll-answer",
    AnswerViewSet,
    base_name="answer")

urlpatterns = api_v1_router.urls

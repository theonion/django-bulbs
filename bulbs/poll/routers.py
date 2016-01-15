from rest_framework.routers import DefaultRouter

from .viewsets import PollViewSet, AnswerViewSet

router = DefaultRouter(trailing_slash=True)
router.register("polls", PollViewSet, "poll")
router.register("answers", AnswerViewSet, "answer")

from rest_framework.routers import DefaultRouter
from bulbs.poll.viewsets import PollViewSet

router = DefaultRouter(trailing_slash=True)
router.register('polls', PollViewSet, 'poll')

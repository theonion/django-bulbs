from rest_framework.routers import DefaultRouter
from bulbs.poll.viewsets import PollViewset

router = DefaultRouter(trailing_slash=True)
router.register('polls', PollViewSet, 'poll')

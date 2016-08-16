from bulbs.serializer_registry.registry import DataSerializerRegistry

from .data_serializers import GuideToParentSerializer, GuideToChildSerializer


GUIDE_TO_HOMEPAGE = 'GUIDE_TO_HOMEPAGE'
GUIDE_TO_ENTRY = 'GUIDE_TO_ENTRY'


registry = DataSerializerRegistry()
registry.register(GUIDE_TO_HOMEPAGE, 'Guide To Homepage', GuideToParentSerializer)
registry.register(GUIDE_TO_ENTRY, 'Guide To Entry', GuideToChildSerializer)

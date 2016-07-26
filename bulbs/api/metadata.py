from rest_framework.metadata import SimpleMetadata

from bulbs.infographics.metadata import InfographicMetadata
from bulbs.infographics.utils import get_infographics_serializer
from bulbs.super_features.metadata import BaseSuperFeatureMetadata
from bulbs.super_features.utils import get_superfeature_serializer


SUPERFEATURE_SERIALIZER = get_superfeature_serializer()
INFOGRAPHICS_SERIALIZER = get_infographics_serializer()


class PolymorphicContentMetadata(SimpleMetadata):

    serializer_lookup = {
        INFOGRAPHICS_SERIALIZER: InfographicMetadata(),
        SUPERFEATURE_SERIALIZER: BaseSuperFeatureMetadata()
    }

    def determine_metadata(self, request, view):
        if hasattr(view, "get_serializer_class"):
            serializer_class = view.get_serializer_class()
            metadata = self.serializer_lookup.get(serializer_class, None)
            if metadata:
                return metadata.determine_metadata(request, view)
        # TODO: Spike out why we included this generic (and bad) response.
        return {"status": "ok"}

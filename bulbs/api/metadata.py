from rest_framework.metadata import SimpleMetadata

from bulbs.infographics.metadata import InfographicMetadata
from bulbs.infographics.serializers import InfographicSerializer
from bulbs.super_features.utils import get_superfeature_serializer, get_superfeature_metadata


SUPERFEATURE_SERIALIZER = get_superfeature_serializer()
SUPERFEATURE_METADATA = get_superfeature_metadata()


class PolymorphicContentMetadata(SimpleMetadata):

    serializer_lookup = {
        InfographicSerializer: InfographicMetadata(),
        SUPERFEATURE_SERIALIZER: SUPERFEATURE_METADATA()
    }

    def determine_metadata(self, request, view):
        if hasattr(view, "get_serializer_class"):
            serializer_class = view.get_serializer_class()
            metadata = self.serializer_lookup.get(serializer_class, None)
            if metadata:
                return metadata.determine_metadata(request, view)
        # TODO: Spike out why we included this generic (and bad) response.
        return {"status": "ok"}

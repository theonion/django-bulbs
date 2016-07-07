from rest_framework.metadata import SimpleMetadata

from bulbs.infographics.metadata import InfographicMetadata
from bulbs.infographics.serializers import InfographicSerializer


class PolymorphicContentMetadata(SimpleMetadata):

    serializer_lookup = {
        InfographicSerializer: InfographicMetadata()
    }

    def determine_metadata(self, request, view):
        if hasattr(view, "get_serializer_class"):
            serializer_class = view.get_serializer_class()
            metadata = self.serializer_lookup.get(serializer_class, None)
            if metadata:
                return metadata.determine_metadata(request, view)
        # TODO: Spike out why we included this generic (and bad) response.
        return {"status": "ok"}

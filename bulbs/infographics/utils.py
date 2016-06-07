from .enum import InfographicType
from .data_serializers import (
    ComparisonSerializer, ListInfographicDataSerializer, ProConSerializer,
    StrongSideWeakSideSerializer, TimelineSerializer
)


def get_data_serializer(infographic_type):
    serializer = {
        InfographicType.LIST: ListInfographicDataSerializer,
        InfographicType.TIMELINE: TimelineSerializer,
        InfographicType.STRONGSIDE_WEAKSIDE: StrongSideWeakSideSerializer,
        InfographicType.PRO_CON: ProConSerializer,
        InfographicType.COMPARISON: ComparisonSerializer
    }.get(infographic_type, None)
    if serializer is None:
        raise KeyError(
            """The requested Infographic does not have a configured serializer."""
        )
    return serializer

from django.conf import settings


def get_superfeature_serializer():
    from bulbs.super_features.serializers import BaseSuperFeatureSerializer

    serializer = getattr(settings, "BULBS_SUPERFEATURE_SERIALIZER", None)
    if serializer is None:
        return BaseSuperFeatureSerializer
    return serializer


def get_superfeature_metadata():
    from bulbs.super_features.metadata import BaseSuperFeatureMetadata

    metadata = getattr(settings, "BULBS_SUPERFEATURE_METADATA", None)
    if metadata is None:
        return BaseSuperFeatureMetadata
    return metadata


def get_superfeature_choices():
    from bulbs.super_features.models import BASE_CHOICES

    configured_superfeatures = getattr(settings, "BULBS_CUSTOM_SUPERFEATURE_CHOICES", ())
    for sf in configured_superfeatures:
        if type(sf[0]) is not str or type(sf[1]) is not str:
            raise ValueError(
                "Super Feature choices must be a string. {0} is not valid".format(sf)
            )
    return BASE_CHOICES + configured_superfeatures

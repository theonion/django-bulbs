from importlib import import_module

from django.conf import settings


def get_data_serializer(name):
    from bulbs.super_features.models import GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
    from bulbs.super_features.data_serializers import (GuideToChildSerializer,
                                                       GuideToParentSerializer)
    serializer = {
        GUIDE_TO_HOMEPAGE: GuideToParentSerializer,
        GUIDE_TO_ENTRY: GuideToChildSerializer
    }.get(name, None)
    if serializer is None:
        raise KeyError('The requested SuperFeature does not have a registered serializer')

    return serializer


def get_superfeature_model():
    module = getattr(settings, "BULBS_SUPERFEATURE_MODEL_MODULE", None)
    model = getattr(settings, "BULBS_SUPERFEATURE_MODEL", None)
    if model is None or module is None:
        from bulbs.super_features.models import BaseSuperFeature
        return BaseSuperFeature
    else:
        # NOTE: import serializer module & then evaluate based on serializer name
        mod = import_module(module)  # NOQA
        return getattr(mod, model)
        # return eval("{0}.{1}".format('mod', model))


def get_superfeature_serializer():
    module = getattr(settings, "BULBS_SUPERFEATURE_SERIALIZER_MODULE", None)
    serializer = getattr(settings, "BULBS_SUPERFEATURE_SERIALIZER", None)
    if serializer is None or module is None:
        from bulbs.super_features.serializers import BaseSuperFeatureSerializer
        return BaseSuperFeatureSerializer
    else:
        # NOTE: import serializer module & then evaluate based on serializer name
        mod = import_module(module)  # NOQA
        return getattr(mod, serializer)
        # return eval("{0}.{1}".format('mod', serializer))


def get_superfeature_partial_serializer():
    module = getattr(settings, "BULBS_SUPERFEATURE_SERIALIZER_MODULE", None)
    serializer = getattr(settings, "BULBS_SUPERFEATURE_PARTIAL_SERIALIZER", None)
    if serializer is None or module is None:
        from bulbs.super_features.serializers import BaseSuperFeaturePartialSerializer
        return BaseSuperFeaturePartialSerializer
    else:
        # NOTE: import serializer module & then evaluate based on serializer name
        mod = import_module(module)  # NOQA
        return getattr(mod, serializer)
        # return eval("{0}.{1}".format('mod', serializer))


def get_superfeature_metadata():
    module = getattr(settings, "BULBS_SUPERFEATURE_METADATA_MODULE", None)
    metadata = getattr(settings, "BULBS_SUPERFEATURE_METADATA", None)
    if metadata is None or module is None:
        from bulbs.super_features.metadata import BaseSuperFeatureMetadata
        return BaseSuperFeatureMetadata
    else:
        # NOTE: import metadata module & then evaluate based on metadata name
        mod = import_module(module)  # NOQA
        return getattr(mod, metadata)
        # return eval("{0}.{1}".format('mod', metadata))


def get_superfeature_choices():
    from bulbs.super_features.models import BASE_CHOICES

    configured_superfeatures = getattr(settings, "BULBS_CUSTOM_SUPERFEATURE_CHOICES", ())
    for sf in configured_superfeatures:
        if type(sf[0]) is not str or type(sf[1]) is not str:
            raise ValueError(
                "Super Feature choices must be a string. {0} is not valid".format(sf)
            )
    return BASE_CHOICES + configured_superfeatures

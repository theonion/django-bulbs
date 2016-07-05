from django.conf import settings


GUIDE_TO = 'GUIDE_TO'
BASE_CHOICES = (
    (GUIDE_TO, 'Guide To'),
)


def get_superfeature_choices():
    configured_superfeatures = getattr(settings, "BULBS_CUSTOM_SUPERFEATURE_CHOICES", ())
    for sf in configured_superfeatures:
        if type(sf[0]) is not str or type(sf[1]) is not str:
            raise ValueError(
                "Super Feature choices must be a string. {0} is not valid".format(sf)
            )
    return BASE_CHOICES + configured_superfeatures

import jsonfield
from django_enumfield import enum

from bulbs.content.models import Content


class InfographicType(enum.Enum):
    LIST = 0
    TIMELINE = 1
    STRONGSIDE_WEAKSIDE = 2
    PRO_CON = 3
    COMPARISON = 4


class BaseInfographic(Content):

    infographic_type = enum.EnumField(InfographicType)
    data = jsonfield.JSONField()

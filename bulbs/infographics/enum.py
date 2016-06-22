from django_enumfield import enum


class InfographicType(enum.Enum):
    LIST = 0
    TIMELINE = 1
    STRONGSIDE_WEAKSIDE = 2
    PRO_CON = 3
    COMPARISON = 4

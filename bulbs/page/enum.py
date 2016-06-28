from django_enumfield import enum


class Status(enum.Enum):
    DRAFT = 0
    PUBLISHED = 1


class TemplateType(enum.Enum):
    pass

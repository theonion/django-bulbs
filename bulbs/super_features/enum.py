from django_enumfield import enum


class Status(enum.Enum):
    DRAFT = 0
    PUBLISHED = 1


class TemplateType(enum.Enum):
    GLOSSARY = 0
    TWO_TYPES = 1
    TIMELINE = 2
    GUIDE_TO = 3
    CUSTOM = 4

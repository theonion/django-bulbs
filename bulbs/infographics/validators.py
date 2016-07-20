import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text


@deconstructible
class ColorValidator(object):
    message = ('Enter a valid hexadecimal color.')
    code = 'invalid'
    color_regex = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        value = force_text(value)
        if not re.compile(self.color_regex, re.IGNORECASE).match(value):
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, ColorValidator) and
            (self.message == other.message),
            (self.code == other.code)
        )

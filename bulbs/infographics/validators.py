from django.core.exceptions import ValidationError
from django.utils import force_text
from django.utils.deconstruct import deconstructible


@deconstructible
class ColorValidator(object):
    message = _('Enter a valid hexadecimal color.')
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        value = force_text(value)
        if not self.color_regex.match(value):
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, ColorValidator) and
            (self.message == other.message),
            (self.code == other.code)
        )

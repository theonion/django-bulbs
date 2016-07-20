import re
import six

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text
from django.utils.functional import SimpleLazyObject


def _lazy_re_compile(regex, flags=0):
    """Lazily compile a regex with flags."""
    def _compile():
        # Compile the regex if it was not passed pre-compiled.
        if isinstance(regex, six.string_types):
            return re.compile(regex, flags)
        else:
            assert not flags, "flags must be empty if regex is passed pre-compiled"
            return regex
    return SimpleLazyObject(_compile)


@deconstructible
class ColorValidator(object):
    message = ('Enter a valid hexadecimal color.')
    code = 'invalid'
    color_regex = _lazy_re_compile(
        r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        re.IGNORECASE
    )

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

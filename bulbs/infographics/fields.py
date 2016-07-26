from rest_framework import serializers

from .validators import ColorValidator


class ColorField(serializers.CharField):

    default_error_messages = {
        'invalid': ('Enter a valid hex value. e.g., #F0F8FF ')
    }

    def __init__(self, **kwargs):
        super(ColorField, self).__init__(**kwargs)
        self.validators.append(
            ColorValidator(message=self.error_messages['invalid'])
        )

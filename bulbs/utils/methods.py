from datetime import date, datetime
from dateutil import tz
from six import string_types, text_type, binary_type

from django.conf import settings
from django.utils import timezone


INVALID_TEMPLATE_CHOICE = """Choices for template values must be non-zero integers."""


def get_central_now():
    utc_now = timezone.now()
    central_tz = tz.gettz('America/Chicago')
    central_now = utc_now.astimezone(central_tz)
    return central_now


def today():
    # catching this because settings.TODAY might literally be None in tests
    # getattr will return None if the value is set to None
    return getattr(settings, "TODAY", get_central_now())


def today_as_utc_datetime():
    """Datetime/Date comparisons aren't great, and someone might configure TODAY, to be a date."""
    now = today()
    if not isinstance(now, datetime) and isinstance(now, date):
        now = datetime.combine(now, datetime.min.time())
        now = now.replace(tzinfo=tz.gettz('UTC'))
    return now


def get_query_params(request):
    try:
        return request.query_params
    except:
        return request.QUERY_PARAMS


def get_request_data(request):
    try:
        return request.data
    except:
        return request.DATA


def is_str(value):
    return isinstance(value, (string_types, text_type, binary_type))


def is_valid_digit(value):
    if isinstance(value, (int, float)):
        return True
    elif is_str(value):
        return value.isdigit()
    return False


def datetime_to_epoch_seconds(value):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
    return (value - epoch).total_seconds()


def get_template_choices():
    configured_templates = getattr(settings, "BULBS_TEMPLATE_CHOICES", ())
    for choice in configured_templates:
        if choice[0] == 0:
            raise ValueError(INVALID_TEMPLATE_CHOICE.format(choice))
        elif type(choice[0]) != int:
            raise ValueError(INVALID_TEMPLATE_CHOICE.format(choice))
    return ((0, None),) + configured_templates

import json
from six import PY3


class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if not PY3 and isinstance(value, str):
            return unicode(value, errors='replace')  # TODO: Be stricter.
        if isinstance(value, set):
            return list(value)
        return super(JsonEncoder, self).default(value)


def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if hasattr(value, 'strftime'):
        if hasattr(value, 'hour'):
            return value.isoformat()
        else:
            return '%sT00:00:00' % value.isoformat()

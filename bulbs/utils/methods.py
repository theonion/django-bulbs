from six import string_types, text_type, binary_type


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

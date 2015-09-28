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

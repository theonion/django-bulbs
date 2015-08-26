def get_query_params(request):
    try:
        return request.query_params
    except:
        return request.QUERY_PARAMS

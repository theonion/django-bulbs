from django.utils.dateparse import parse_datetime


class PromotionMiddleware(object):

    def process_template_response(self, request, response):
        when = None
        if request.method == "GET" and "pzone_preview" in request.GET:
            when = parse_datetime(request.GET["pzone_preview"])

        if when:
            response.context_data["pzone_preview"] = when

        return response

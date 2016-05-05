from django.conf import settings


class AdTargetingMiddleware(object):

    def process_template_response(self, request, response):

        if response.context_data is None:
            return response

        targeting = {}
        if "targeting" in response.context_data:
            targeting = response.context_data["targeting"]

        if "dfp_site" not in targeting:
            targeting["dfp_site"] = settings.DFP_SITE

        if request.method == "GET" and "dfptest" in request.GET:
            targeting["dfp_test"] = request.GET["dfptest"]

        response.context_data["targeting"] = targeting

        return response

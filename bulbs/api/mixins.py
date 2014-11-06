class UncachedResponse(object):
    @property
    def default_response_headers(self):
        return {
            "Allow": ", ".join(self.allowed_methods),
            "Vary": "Accept",
            "Cache-Control": "no-cache"
        }

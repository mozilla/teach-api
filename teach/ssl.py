from django.http import HttpResponsePermanentRedirect

class RedirectToHttpsMiddleware(object):
    def process_request(self, request):
        if not request.is_secure():
            url = 'https://%s%s' % (request.META['HTTP_HOST'], request.path)
            return HttpResponsePermanentRedirect(url)

class HstsMiddleware(object):
    def process_response(self, request, response):
        response["Strict-Transport-Security"] = "max-age=31536000; " \
                                                "includeSubdomains"
        return response

import base64
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponse

class BasicAuthMiddleware(object):
    """
    Middleware that requires a username/password to access the admin
    section of the site. This is *in addition* to the other requirements
    for accessing the admin section of the site.
    """

    def __init__(self):
        if (not hasattr(settings, 'ADMIN_PROTECTION_USERPASS') or
            not settings.ADMIN_PROTECTION_USERPASS):
            raise MiddlewareNotUsed()
        self.userpass = settings.ADMIN_PROTECTION_USERPASS

    def process_request(self, request):
        # https://djangosnippets.org/snippets/2095/
        admin_index = reverse('admin:index')
        if not request.path.startswith(admin_index):
            return
        # https://djangosnippets.org/snippets/243/
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                try:
                    auth = base64.b64decode(auth[1])
                    if auth == self.userpass:
                        return
                except TypeError:
                    pass

        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Admin"'
        return response

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import django_browserid.base

from . import webmaker

def get_verifier():
    return django_browserid.base.RemoteVerifier()

@csrf_exempt
def persona_assertion_to_api_token(request, get_verifier=get_verifier):
    origin = request.META.get('HTTP_ORIGIN')
    if origin not in settings.API_PERSONA_ORIGINS:
        if not (settings.DEBUG and settings.API_PERSONA_ORIGINS == ['*']):
            return HttpResponse('invalid origin', status=403)
    res = HttpResponse()
    res['access-control-allow-origin'] = origin
    assertion = request.POST.get('assertion')
    if not assertion:
        res.status_code = 400
        res.content = 'assertion required'
        return res
    verifier = get_verifier()
    result = verifier.verify(assertion, origin)
    if not result:
        res.status_code = 403
        res.content = 'invalid assertion'
        return res
    email = result['email']
    backend = webmaker.WebmakerBrowserIDBackend()
    raise NotImplementedError()

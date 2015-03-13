import json
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import django_browserid.base
from rest_framework.authtoken.models import Token

from . import webmaker

def get_verifier():
    return django_browserid.base.RemoteVerifier()

@require_POST
@csrf_exempt
def persona_assertion_to_api_token(request, backend=None):
    origin = request.META.get('HTTP_ORIGIN')
    valid_origins = settings.CORS_API_PERSONA_ORIGINS
    if not origin or origin not in valid_origins:
        if not (settings.DEBUG and valid_origins == ['*']):
            return HttpResponse('invalid origin', status=403)
    res = HttpResponse()
    res['access-control-allow-origin'] = origin
    assertion = request.POST.get('assertion')
    if not assertion:
        res.status_code = 400
        res.content = 'assertion required'
        return res
    if backend is None:
        backend = webmaker.WebmakerBrowserIDBackend()
    user = backend.authenticate(assertion=assertion, audience=origin,
                                request=request)
    if user is None:
        res.status_code = 403
        res.content = 'invalid assertion or email'
        return res
    token, created = Token.objects.get_or_create(user=user)
    res['content-type'] = 'application/json'
    res.content = json.dumps({
        'token': token.key,
        'username': user.username
    })
    return res

def api_introduction(request):
    return render(request, 'teach/api-introduction.html')

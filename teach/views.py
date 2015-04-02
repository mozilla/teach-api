import json
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import django_browserid.base
from rest_framework import routers
from rest_framework.authtoken.models import Token

from . import webmaker

def get_verifier():
    return django_browserid.base.RemoteVerifier()

def check_origin(request):
    origin = request.META.get('HTTP_ORIGIN')
    valid_origins = settings.CORS_API_PERSONA_ORIGINS
    if not origin or origin not in valid_origins:
        if not (settings.DEBUG and valid_origins == ['*']):
            return None
    res = HttpResponse()
    res['access-control-allow-origin'] = origin
    return res

def json_response(res, data):
    res['content-type'] = 'application/json'
    res.content = json.dumps(data)
    return res

def info_for_user(res, user):
    token, created = Token.objects.get_or_create(user=user)
    return json_response(res, {
        'token': token.key,
        'username': user.username
    })

@require_GET
def get_status(request):
    res = check_origin(request)
    if res is None:
        return HttpResponse('invalid origin', status=403)
    res['access-control-allow-credentials'] = 'true'
    if request.user.is_authenticated():
        return info_for_user(res, request.user)
    return json_response(res, {
        'username': None
    })

@require_POST
@csrf_exempt
def persona_assertion_to_api_token(request, backend=None):
    res = check_origin(request)
    if res is None:
        return HttpResponse('invalid origin', status=403)
    assertion = request.POST.get('assertion')
    if not assertion:
        res.status_code = 400
        res.content = 'assertion required'
        return res
    if backend is None: backend = webmaker.WebmakerBrowserIDBackend()
    user = backend.authenticate(assertion=assertion,
                                audience=request.META.get('HTTP_ORIGIN'),
                                request=request)
    if user is None:
        res.status_code = 403
        res.content = 'invalid assertion or email'
        return res
    return info_for_user(res, user)

def api_introduction(request):
    if request.user.is_authenticated():
        token, created = Token.objects.get_or_create(user=request.user)
        token = token.key
    else:
        token = '0eafe9fb9111e93bdc67a899623365a21f69065b'
    return render(request, 'teach/api-introduction.html', {
        'ORIGIN': settings.ORIGIN,
        'CORS_API_PERSONA_ORIGINS': settings.CORS_API_PERSONA_ORIGINS,
        'token': token
    })

# This is a really weird way of defining our own API root docs, but
# it seems to be the only known one: http://stackoverflow.com/q/17496249
class TeachRouter(routers.DefaultRouter):
    def get_api_root_view(self):
        api_root_view = super(TeachRouter, self).get_api_root_view()
        ApiRootClass = api_root_view.cls

        class APIRoot(ApiRootClass):
            """
            This is the root of the Mozilla Learning API. Follow
            links below to explore the documentation.

            You can also view the [API Introduction][intro] to
            learn how to authenticate with the API if needed.

              [intro]: /api-introduction/
            """

            pass

        return APIRoot.as_view()

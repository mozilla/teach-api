import json
import urlparse
import django.contrib.auth
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils.crypto import get_random_string
import django_browserid.base
import requests
from rest_framework import routers
from rest_framework.authtoken.models import Token

from . import webmaker, new_webmaker
from .new_webmaker import get_idapi_url

def get_verifier():
    return django_browserid.base.RemoteVerifier()

def get_origin(url):
    """
    Returns the origin (http://www.w3.org/Security/wiki/Same_Origin_Policy)
    of the given URL.

    Examples:

        >>> get_origin('http://foo/blarg')
        'http://foo'
        >>> get_origin('https://foo')
        'https://foo'
        >>> get_origin('http://foo:123/blarg')
        'http://foo:123'

    If the URL isn't http or https, it returns None:

        >>> get_origin('')
        >>> get_origin('weirdprotocol://lol.com')

    """

    info = urlparse.urlparse(url)
    if info.scheme not in ['http', 'https']:
        return None
    return '%s://%s' % (info.scheme, info.netloc)

def validate_callback(callback):
    origin = get_origin(callback)
    valid_origins = settings.CORS_API_LOGIN_ORIGINS
    if origin and origin in valid_origins:
        return callback
    if settings.DEBUG and valid_origins == ['*']:
        return callback
    return None

def set_callback(request):
    callback = validate_callback(request.GET.get('callback', ''))
    if (not callback
        and 'next' in request.GET
        and request.GET['next'].startswith('/')):
        callback = settings.ORIGIN + request.GET['next']
    if callback:
        request.session['oauth2_callback'] = callback

def oauth2_authorize(request):
    set_callback(request)
    request.session['oauth2_state'] = get_random_string(length=32)
    action = request.GET.get('action')

    if action not in ['signup', 'signin']:
        action = 'signin'

    return HttpResponseRedirect(get_idapi_url("/login/oauth/authorize", {
        'client_id': settings.IDAPI_CLIENT_ID,
        'response_type': 'code',
        'scopes': 'user email',
        'action': action,
        'state': request.session['oauth2_state']
    }))

def login_error(request, error_code, callback):
    try:
        import newrelic.agent
        newrelic.agent.record_custom_metric('Custom/OAuth_%s' % error_code, 1)
    except ImportError:
        pass
    return render(request, 'teach/oauth2_callback_error.html', {
        'error_code': error_code,
        'callback': callback
    })

def oauth2_callback(request):
    callback = request.session.get('oauth2_callback',
                                   '%s/' % settings.TEACH_SITE_URL)
    expected_state = request.session.get('oauth2_state')
    state = request.GET.get('state')
    code = request.GET.get('code')
    if request.GET.get('logout') == 'true':
        django.contrib.auth.logout(request)
        return HttpResponseRedirect(callback)
    if state is None:
        return login_error(request, 'missing_state', callback)
    if expected_state is None:
        return login_error(request, 'missing_session_state', callback)
    if state != expected_state:
        return login_error(request, 'invalid_state', callback)
    if code is None:
        return login_error(request, 'missing_code', callback)

    user = django.contrib.auth.authenticate(webmaker_oauth2_code=code)
    if user is None:
        return login_error(request, 'invalid_code_or_idapi_err', callback)
    del request.session['oauth2_state']

    django.contrib.auth.login(request, user)

    return HttpResponseRedirect(callback)

def oauth2_logout(request):
    set_callback(request)
    return HttpResponseRedirect(get_idapi_url("/logout", {
        'client_id': settings.IDAPI_CLIENT_ID
    }))

def check_origin(request):
    origin = request.META.get('HTTP_ORIGIN')
    valid_origins = settings.CORS_API_LOGIN_ORIGINS
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
    body = {
        'token': token.key,
        'username': user.username
    }
    if user.is_staff:
        body['admin_url'] = '%s%s' % (settings.ORIGIN,
                                      reverse('admin:index'))
    return json_response(res, body)

@require_POST
@csrf_exempt
def logout(request):
    res = check_origin(request)
    if res is None:
        return HttpResponse('invalid origin', status=403)
    res['access-control-allow-credentials'] = 'true'
    django.contrib.auth.logout(request)
    return json_response(res, {
        'username': None
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
        'CORS_API_LOGIN_ORIGINS': settings.CORS_API_LOGIN_ORIGINS,
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

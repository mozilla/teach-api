import urllib
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

def expect(a, b):
    if a != b:
        print "Warning: Expected %s to equal %s." % (a, b)

@require_GET
def authorize(request):
    expect(request.GET.get('client_id'), settings.IDAPI_CLIENT_ID)
    expect(request.GET.get('response_type'), 'code')
    expect(request.GET.get('scopes'), 'user email')

    url = reverse('teach.views.oauth2_callback')
    qs = urllib.urlencode({
        'state': request.GET['state'],
        'code': 'fake_oauth2_code',
    })
    return HttpResponseRedirect('%s?%s' % (url, qs))

@csrf_exempt
@require_POST
def access_token(request):
    expect(request.POST.get('code'), 'fake_oauth2_code')
    expect(request.POST.get('client_id'), settings.IDAPI_CLIENT_ID)
    expect(request.POST.get('client_secret'), settings.IDAPI_CLIENT_SECRET)
    expect(request.POST.get('grant_type'), 'authorization_code')

    res = HttpResponse()
    res['content-type'] = 'application/json'
    res.content = json.dumps({
        'access_token': 'fake_oauth2_access_token'
    })

    return res

@require_GET
def user(request):
    expect(request.META.get('HTTP_AUTHORIZATION'),
           'token fake_oauth2_access_token')

    res = HttpResponse()
    res['content-type'] = 'application/json'
    res.content = json.dumps({
        'username': settings.IDAPI_FAKE_OAUTH2_USERNAME,
        'email': settings.IDAPI_FAKE_OAUTH2_EMAIL
    })

    return res

@require_GET
def logout(request):
    url = reverse('teach.views.oauth2_callback')
    qs = 'logout=true'
    return HttpResponseRedirect('%s?%s' % (url, qs))

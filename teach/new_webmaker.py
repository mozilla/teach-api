import urllib
import requests
import logging
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger('teach.oauth2')

def get_idapi_url(path, query=None):
    if query is not None:
        qs = urllib.urlencode(query)
        path = '%s?%s' % (path, qs)
    if settings.IDAPI_ENABLE_FAKE_OAUTH2:
        return '%s/fake_oauth2%s' % (settings.ORIGIN, path)
    else:
        return '%s%s' % (settings.IDAPI_URL, path)

def exchange_code_for_access_token(code):
    payload = {
        'client_id': settings.IDAPI_CLIENT_ID,
        'client_secret': settings.IDAPI_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code
    }
    token_req = requests.post(get_idapi_url('/login/oauth/access_token'),
                              data=payload)
    if token_req.status_code != 200:
        logger.warn('POST /login/oauth/access_token returned %s '
                    'w/ content %s' % (
            token_req.status_code,
            repr(token_req.content)
        ))
        return None
    return token_req.json()['access_token']

def get_user_info(access_token):
    user_req = requests.get(get_idapi_url('/user'), headers={
        'authorization': 'token %s' % access_token
    })
    if user_req.status_code != 200:
        logger.warn('GET /user returned %s '
                    'w/ content %s and access token %s' % (
            user_req.status_code,
            repr(user_req.content),
            access_token
        ))
        return None
    return user_req.json()

def get_or_create_user(username, email, **kwargs):
    users = User.objects.filter(username=username)
    if len(users) == 0:
        user = User.objects.create_user(username, email)
        return user
    else:
        return users[0]

class WebmakerOAuth2Backend(object):
    def authenticate(self, webmaker_oauth2_code=None, **kwargs):
        if webmaker_oauth2_code is None:
            return None

        access_token = exchange_code_for_access_token(webmaker_oauth2_code)
        if access_token is None:
            return None

        user_info = get_user_info(access_token)
        if user_info is None:
            return None

        return get_or_create_user(**user_info)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

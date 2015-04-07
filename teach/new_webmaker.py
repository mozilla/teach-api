import urllib
import requests
from django.contrib.auth.models import User
from django.conf import settings

def get_idapi_url(path, query=None):
    if query is not None:
        qs = urllib.urlencode(query)
        path = '%s?%s' % (path, qs)
    if settings.IDAPI_ENABLE_FAKE_OAUTH2:
        return '%s/fake_oauth2%s' % (settings.ORIGIN, path)
    else:
        return '%s%s' % (settings.IDAPI_URL, path)

class WebmakerOAuth2Backend(object):
    def authenticate(self, webmaker_oauth2_code=None, **kwargs):
        if webmaker_oauth2_code is None:
            return None

        payload = {
            'client_id': settings.IDAPI_CLIENT_ID,
            'client_secret': settings.IDAPI_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': webmaker_oauth2_code
        }
        token_req = requests.post(get_idapi_url('/login/oauth/access_token'),
                                  data=payload)
        access_token = token_req.json()['access_token']
        user_req = requests.get(get_idapi_url('/user'), headers={
            'authorization': 'token %s' % access_token
        })
        user_info = user_req.json()

        users = User.objects.filter(username=user_info['username'])
        if len(users) == 0:
            user = User.objects.create_user(user_info['username'],
                                            user_info['email'])
            return user
        else:
            return users[0]

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

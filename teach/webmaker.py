import requests
from django.conf import settings
from django_browserid.auth import BrowserIDBackend

def get_user_info_for_email(email):
    if settings.LOGINAPI_AUTH is None:
        return None

    req = requests.get(
        settings.LOGINAPI_URL + '/user/email/%s' % email,
        auth=tuple(settings.LOGINAPI_AUTH.split(':'))
    )
    if req.status_code == 404:
        return None
    if req.status_code == 200:
        return req.json()['user']
    raise Exception('got status %d when querying for email %s' % (
        req.status_code,
        email
    ))

def get_username_for_email(email):
    info = get_user_info_for_email(email)
    if info is None:
        return None
    return info['username']

class WebmakerBrowserIDBackend(BrowserIDBackend):
    def create_user(self, email):
        username = get_username_for_email(email)
        if username is None:
            raise Exception('no username for %s' % email)
        return self.User.objects.create_user(username, email)

    def is_valid_email(self, email):
        users = self.User.objects.filter(email=email)
        if len(users):
            return True
        username = get_username_for_email(email)
        return (username is not None)

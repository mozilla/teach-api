import httmock
from django.test import TestCase
from django.test.utils import override_settings

from .. import webmaker

@override_settings(LOGINAPI_AUTH='foo:bar',
                   LOGINAPI_URL='https://login')
class GetUsernameForEmailTests(TestCase):
    @override_settings(LOGINAPI_AUTH=None)
    def test_always_returns_none_with_no_auth_info(self):
        info = webmaker.get_username_for_email('foo')
        self.assertEqual(info, None)

    def test_returns_none_on_404(self):
        def match_404(url, request):
            self.assertEqual(request.url, 'https://login/user/email/404')
            self.assertEqual(request.headers['authorization'],
                             'Basic Zm9vOmJhcg==')
            return httmock.response(404)

        with httmock.HTTMock(match_404):
            username = webmaker.get_username_for_email('404')
            self.assertEqual(username, None)

    def test_returns_info_on_200(self):
        def match_200(url, request):
            self.assertEqual(request.url, 'https://login/user/email/200')
            return httmock.response(200, {
                'user': {'username': 'boop'}
            }, {
                'content-type': 'application/json'
            })

        with httmock.HTTMock(match_200):
            username = webmaker.get_username_for_email('200')
            self.assertEqual(username, 'boop')

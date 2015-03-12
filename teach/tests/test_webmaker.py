import httmock
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User

from .. import webmaker

def respond_with_username(username):
    return httmock.response(200, {
        'user': {'username': username}
    }, {
        'content-type': 'application/json'
    })

@override_settings(LOGINAPI_AUTH='foo:bar',
                   LOGINAPI_URL='https://login')
class WebmakerBrowserIDBackendTests(TestCase):
    def mock_affirmative_response(self, url, request):
        return respond_with_username('boop')

    def mock_negative_response(self, url, request):
        return httmock.response(404)

    def test_create_user_works(self):
        backend = webmaker.WebmakerBrowserIDBackend()
        with httmock.HTTMock(self.mock_affirmative_response):
            user = backend.create_user('example@example.org')
            self.assertEqual(user.username, 'boop')
            self.assertEqual(user.email, 'example@example.org')

    def test_is_valid_email_returns_true_when_user_already_exists(self):
        user = User.objects.create_user('blah', 'blah@example.org')
        backend = webmaker.WebmakerBrowserIDBackend()
        with httmock.HTTMock(self.mock_negative_response):
            self.assertTrue(backend.is_valid_email('blah@example.org'))

    def test_is_valid_email_returns_true(self):
        backend = webmaker.WebmakerBrowserIDBackend()
        with httmock.HTTMock(self.mock_affirmative_response):
            self.assertTrue(backend.is_valid_email('example@example.org'))

    def test_is_valid_email_returns_false(self):
        backend = webmaker.WebmakerBrowserIDBackend()
        with httmock.HTTMock(self.mock_negative_response):
            self.assertFalse(backend.is_valid_email('example@example.org'))

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
            return respond_with_username('boop')

        with httmock.HTTMock(match_200):
            username = webmaker.get_username_for_email('200')
            self.assertEqual(username, 'boop')

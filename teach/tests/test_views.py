import json
import doctest
from django.test import TestCase, RequestFactory, Client
from django.test.utils import override_settings
from django.contrib.auth.models import User, AnonymousUser
from django_browserid.base import MockVerifier, VerificationResult
import mock

from .. import views
from .. import webmaker

class FakeBrowserIDBackend(webmaker.WebmakerBrowserIDBackend):
    def __init__(self, email):
        super(FakeBrowserIDBackend, self).__init__()
        self.__fake_email = email

    def get_verifier(self):
        return MockVerifier(self.__fake_email)

class ViewSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()

    def login(self):
        User.objects.create_user('foo', 'foo@example.org', 'pass')
        self.assertTrue(self.client.login(username='foo',
                                          password='pass'))

    def verify_200(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_root(self):
        self.verify_200('/api/')

    def test_api_introduction(self):
        self.verify_200('/api-introduction/')

    def test_authenticated_api_introduction(self):
        self.login()
        self.verify_200('/api-introduction/')

class CorsTests(TestCase):
    def test_api_paths_have_cors_enabled(self):
        c = Client()
        response = c.get('/api/', HTTP_ORIGIN='http://foo.org')
        self.assertEqual(response['access-control-allow-origin'], '*')

    def test_non_api_paths_have_cors_disabled(self):
        c = Client()
        response = c.get('/admin/', HTTP_ORIGIN='http://foo.org')
        self.assertFalse('access-control-allow-origin' in response)

@override_settings(CORS_API_LOGIN_ORIGINS=['http://example.org'],
                   DEBUG=False)
class AuthLogoutTests(TestCase):
    @mock.patch('django.contrib.auth.logout')
    def test_logout_works(self, logout):
        factory = RequestFactory()
        req = factory.post('/', HTTP_ORIGIN='http://example.org')
        response = views.logout(req)
        self.assertTrue(logout.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['access-control-allow-origin'],
                         'http://example.org')
        self.assertEqual(response['access-control-allow-credentials'],
                         'true')
        self.assertEqual(json.loads(response.content), {
            'username': None
        })

@override_settings(CORS_API_LOGIN_ORIGINS=['http://example.org'],
                   DEBUG=False)
class AuthStatusTests(TestCase):
    def setUp(self):
        self.view = views.get_status
        self.factory = RequestFactory()
        self.user = User.objects.create_user('foo', 'foo@example.org')

    def get_request(self, user=None, **kwargs):
        if user is None:
            user = AnonymousUser()
        req = self.factory.get('/', **kwargs)
        req.user = user
        return req

    def test_403_when_origin_is_absent(self):
        req = self.get_request()
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    def test_403_when_origin_is_not_whitelisted(self):
        req = self.get_request(HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    @override_settings(CORS_API_LOGIN_ORIGINS=['*'], DEBUG=True)
    def test_any_origin_allowed_when_debugging(self):
        req = self.get_request()
        response = self.view(req)
        self.assertEqual(response.status_code, 200)

    @override_settings(CORS_API_LOGIN_ORIGINS=['*'], DEBUG=False)
    def test_any_origin_not_allowed_when_not_debugging(self):
        req = self.get_request(HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    def test_cors_header_is_valid(self):
        req = self.get_request(HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        self.assertEqual(response['access-control-allow-origin'],
                         'http://example.org')
        self.assertEqual(response['access-control-allow-credentials'],
                         'true')

    def test_username_is_none_when_logged_out(self):
        req = self.get_request(HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'username': None
        })

    def test_info_is_provided_when_logged_in(self):
        req = self.get_request(user=self.user,
                               HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['username'], 'foo')
        self.assertRegexpMatches(content['token'], r'^[0-9a-f]+$')

@override_settings(CORS_API_LOGIN_ORIGINS=['http://example.org'],
                   DEBUG=False)
class PersonaTokenToAPITokenTests(TestCase):
    def setUp(self):
        self.view = views.persona_assertion_to_api_token
        self.factory = RequestFactory()

    def test_403_when_origin_is_absent(self):
        req = self.factory.post('/')
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    def test_403_when_origin_is_not_whitelisted(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    @override_settings(CORS_API_LOGIN_ORIGINS=['*'], DEBUG=True)
    def test_any_origin_allowed_when_debugging(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'assertion required')

    @override_settings(CORS_API_LOGIN_ORIGINS=['*'], DEBUG=False)
    def test_any_origin_not_allowed_when_not_debugging(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'invalid origin')

    def test_cors_header_is_valid(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        self.assertEqual(response['access-control-allow-origin'],
                         'http://example.org')

    def test_400_when_assertion_not_present(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'assertion required')

    def request_with_assertion(self, email):
        req = self.factory.post('/', {
            'assertion': 'foo'
        }, HTTP_ORIGIN='http://example.org')
        response = self.view(req, backend=FakeBrowserIDBackend(email))
        self.assertEqual(response['access-control-allow-origin'],
                         'http://example.org')
        if response['Content-Type'] == 'application/json':
            response.json = json.loads(response.content)
        return response

    def test_403_when_assertion_invalid(self):
        response = self.request_with_assertion(email=None)
        self.assertEqual(response.content, 'invalid assertion or email')

    def test_200_when_assertion_valid_and_account_exists(self):
        User.objects.create_user('foo', 'foo@example.org')
        response = self.request_with_assertion(email='foo@example.org')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'foo')
        self.assertRegexpMatches(response.json['token'], r'^[0-9a-f]+$')

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(views))
    return tests

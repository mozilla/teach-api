import json
import urlparse
import urllib
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
        self.assertTrue('admin_url' not in content)
        self.assertEqual(content['username'], 'foo')
        self.assertRegexpMatches(content['token'], r'^[0-9a-f]+$')

    @override_settings(ORIGIN='http://server')
    def test_admin_url_is_provided_when_staff_is_logged_in(self):
        self.user.is_staff = True
        req = self.get_request(user=self.user,
                               HTTP_ORIGIN='http://example.org')
        response = self.view(req)
        content = json.loads(response.content)
        self.assertEqual(content['admin_url'], 'http://server/admin/')

def get_query(url):
    urlinfo = urlparse.urlparse(url)
    return dict(urlparse.parse_qsl(urlinfo.query))

@override_settings(
    DEBUG=False,
    CORS_API_LOGIN_ORIGINS=['http://frontend'],
    TEACH_SITE_URL='http://teach',
    IDAPI_ENABLE_FAKE_OAUTH2=False,
    IDAPI_URL='http://idapi',
    IDAPI_CLIENT_ID='clientid'
)
class OAuth2EndpointTests(TestCase):
    def assertCallbackErrorCode(self, response, error_code):
        self.assertRegexpMatches(response.content,
                                 r'Error code: %s' % error_code)

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    def test_authorize_redirects_to_idapi(self, get_random_string):
        response = self.client.get('/auth/oauth2/authorize')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_query(response['location']), {
            'client_id': 'clientid',
            'response_type': 'code',
            'scopes': 'user email',
            'action': 'signin',
            'state': 'abcd'
        })
        get_random_string.assert_called_with(length=32)

    def test_authorize_passes_action_signup(self):
        response = self.client.get('/auth/oauth2/authorize?action=signup')
        self.assertEqual(get_query(response['location'])['action'], 'signup')

    def test_authorize_ignores_invalid_action(self):
        response = self.client.get('/auth/oauth2/authorize?action=LOL')
        self.assertEqual(get_query(response['location'])['action'], 'signin')

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    def test_authorize_stores_oauth2_state(self, _):
        self.client.get('/auth/oauth2/authorize')
        self.assertEqual(self.client.session['oauth2_state'], 'abcd')

    @override_settings(ORIGIN='http://teach')
    def test_authorize_remembers_valid_next(self):
        qs = urllib.urlencode({'next': '/boop'})
        response = self.client.get('/auth/oauth2/authorize?%s' % qs)
        self.assertEqual(self.client.session['oauth2_callback'],
                         'http://teach/boop')

    def test_authorize_ignores_invalid_next(self):
        qs = urllib.urlencode({'next': 'http://evil.com/bad'})
        response = self.client.get('/auth/oauth2/authorize?%s' % qs)
        self.assertFalse('oauth2_callback' in self.client.session)

    def test_authorize_remembers_valid_callback(self):
        qs = urllib.urlencode({'callback': 'http://frontend/blah'})
        response = self.client.get('/auth/oauth2/authorize?%s' % qs)
        self.assertEqual(self.client.session['oauth2_callback'],
                         'http://frontend/blah')

    def test_authorize_ignores_invalid_callback(self):
        qs = urllib.urlencode({'callback': 'http://evil.com/bad'})
        response = self.client.get('/auth/oauth2/authorize?%s' % qs)
        self.assertFalse('oauth2_callback' in self.client.session)

    def test_callback_reports_missing_state_in_querystring(self):
        response = self.client.get('/auth/oauth2/callback')
        self.assertCallbackErrorCode(response, 'missing_state')

    def test_callback_fails_when_state_missing_from_session(self):
        response = self.client.get('/auth/oauth2/callback?state=bad')
        self.assertCallbackErrorCode(response, 'missing_session_state')

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    def test_callback_fails_when_state_is_incorrect(self, _):
        self.client.get('/auth/oauth2/authorize')
        response = self.client.get('/auth/oauth2/callback?state=bad')
        self.assertCallbackErrorCode(response, 'invalid_state')

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    def test_callback_reports_missing_code(self, _):
        self.client.get('/auth/oauth2/authorize')
        response = self.client.get('/auth/oauth2/callback?state=abcd')
        self.assertCallbackErrorCode(response, 'missing_code')

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    @mock.patch('django.contrib.auth.authenticate', return_value=None)
    def test_callback_reports_invalid_code_or_idapi_err(self, authmock, _):
        self.client.get('/auth/oauth2/authorize')
        response = self.client.get('/auth/oauth2/callback?state=abcd&code=a')
        self.assertCallbackErrorCode(response, 'invalid_code_or_idapi_err')
        authmock.assert_called_with(webmaker_oauth2_code='a')

    @mock.patch('teach.views.get_random_string', return_value='abcd')
    def test_callback_logs_user_in_and_redirects(self, _):
        user = User.objects.create_user('foo', 'foo@example.org')
        user.backend = 'fake string so auth.login() does not throw'
        self.client.get('/auth/oauth2/authorize')
        with mock.patch('django.contrib.auth.authenticate',
                        return_value=user) as authmock:
            response = self.client.get('/auth/oauth2/callback?'
                                       'state=abcd&code=cool')
            authmock.assert_called_with(webmaker_oauth2_code='cool')
            self.assertTrue('_auth_user_id' in self.client.session)
            self.assertFalse('oauth2_state' in self.client.session)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['location'], 'http://teach/')

    def test_callback_logs_user_out_and_redirects(self):
        user = User.objects.create_user('foo',
                                        'foo@example.org',
                                        password='blah')
        self.client.login(username='foo', password='blah')
        self.assertNotEqual(self.client.session.keys(), [])
        response = self.client.get('/auth/oauth2/callback?logout=true')
        self.assertEqual(self.client.session.keys(), [])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://teach/')

    def test_logout_redirects_to_idapi(self):
        response = self.client.get('/auth/oauth2/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],
                         'http://idapi/logout?client_id=clientid')

    def test_logout_remembers_valid_callback(self):
        qs = urllib.urlencode({'callback': 'http://frontend/blah'})
        response = self.client.get('/auth/oauth2/logout?%s' % qs)
        self.assertEqual(self.client.session['oauth2_callback'],
                         'http://frontend/blah')

    def test_logout_ignores_invalid_callback(self):
        qs = urllib.urlencode({'callback': 'http://evil.com/bad'})
        response = self.client.get('/auth/oauth2/logout?%s' % qs)
        self.assertFalse('oauth2_callback' in self.client.session)

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

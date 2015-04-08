import httmock
import urlparse
import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User

from .. import new_webmaker as nw

@override_settings(
    IDAPI_ENABLE_FAKE_OAUTH2=False,
    IDAPI_URL='http://idapi',
    IDAPI_CLIENT_ID='clientid',
    IDAPI_CLIENT_SECRET='clientsecret'
)
class WebmakerOAuth2BackendTests(TestCase):
    def mock_negative_response(self, url, request):
        return httmock.response(404, "nope")

    @mock.patch('teach.new_webmaker.logger.warn')
    def test_exchange_code_for_access_token_returns_none_on_failure(self, m):
        with httmock.HTTMock(self.mock_negative_response):
            self.assertEqual(nw.exchange_code_for_access_token('u'), None)
        m.assert_called_with('POST /login/oauth/access_token returned 404 '
                             'w/ content \'nope\'')

    def test_exchange_code_for_access_token_returns_token_on_success(self):
        def mock_response(url, request):
            self.assertEqual(request.url,
                             'http://idapi/login/oauth/access_token')
            body = dict(urlparse.parse_qsl(request.body))
            self.assertEqual(body, {
                'code': 'foo',
                'client_id': 'clientid',
                'client_secret': 'clientsecret',
                'grant_type': 'authorization_code'
            })
            return httmock.response(200, {'access_token': 'lol'}, {
                'content-type': 'application/json'
            })

        with httmock.HTTMock(mock_response):
            self.assertEqual(nw.exchange_code_for_access_token('foo'), 'lol')

    @mock.patch('teach.new_webmaker.logger.warn')
    def test_get_user_info_returns_none_on_failure(self, m):
        with httmock.HTTMock(self.mock_negative_response):
            self.assertEqual(nw.get_user_info('tok'), None)
        m.assert_called_with('GET /user returned 404 w/ content \'nope\' '
                             'and access token tok')

    def test_get_user_info_returns_info_on_success(self):
        def mock_response(url, request):
            self.assertEqual(request.url, 'http://idapi/user')
            self.assertEqual(request.headers['authorization'], 'token tok')
            return httmock.response(200, {
                'username': 'foo',
                'email': 'foo@example.org'
            }, {
                'content-type': 'application/json'
            })

        with httmock.HTTMock(mock_response):
            self.assertEqual(nw.get_user_info('tok'), {
                'username': 'foo',
                'email': 'foo@example.org'
            })

    def test_get_idapi_url_adds_querystring(self):
        self.assertEqual(nw.get_idapi_url('/foo', {'bar': 'hi'}),
                         'http://idapi/foo?bar=hi')

    def test_get_idapi_url_accepts_no_query(self):
        self.assertEqual(nw.get_idapi_url('/foo'), 'http://idapi/foo')

    @override_settings(
        ORIGIN='http://me',
        IDAPI_ENABLE_FAKE_OAUTH2=True
    )
    def test_get_idapi_url_returns_fake_oauth2_url(self):
        self.assertEqual(nw.get_idapi_url('/foo'),
                         'http://me/fake_oauth2/foo')

    def test_get_or_create_user_returns_existing_user(self):
        user = User.objects.create_user('foo', 'foo@example.org')
        self.assertEqual(nw.get_or_create_user('foo', 'blah'), user)

    def test_get_or_create_user_creates_new_user(self):
        user = nw.get_or_create_user('foo', 'foo@a.org')
        self.assertEqual(user.username, 'foo')
        self.assertEqual(user.email, 'foo@a.org')

    def test_get_user_returns_none_when_id_is_invalid(self):
        backend = nw.WebmakerOAuth2Backend()
        self.assertEqual(backend.get_user(32434), None)

    def test_get_user_returns_user_when_id_is_valid(self):
        backend = nw.WebmakerOAuth2Backend()
        user = User.objects.create_user('foo', 'foo@example.org')
        self.assertEqual(backend.get_user(user.id), user)

    def test_authenticate_returns_none_when_code_is_none(self):
        backend = nw.WebmakerOAuth2Backend()
        self.assertEqual(backend.authenticate(), None)

    @mock.patch('teach.new_webmaker.exchange_code_for_access_token',
                return_value=None)
    def test_authenticate_returns_none_when_code_is_invalid(self, m):
        backend = nw.WebmakerOAuth2Backend()
        self.assertEqual(backend.authenticate('invalidcode'), None)
        m.assert_called_with('invalidcode')

    @mock.patch('teach.new_webmaker.exchange_code_for_access_token',
                return_value='tok')
    @mock.patch('teach.new_webmaker.get_user_info',
                return_value=None)
    def test_authenticate_returns_none_when_user_info_fails(self, u, a):
        backend = nw.WebmakerOAuth2Backend()
        self.assertEqual(backend.authenticate('validcode'), None)
        a.assert_called_with('validcode')
        u.assert_called_with('tok')

    @mock.patch('teach.new_webmaker.exchange_code_for_access_token',
                return_value='tok')
    @mock.patch('teach.new_webmaker.get_user_info',
                return_value={'username': 'foo',
                              'email': 'foo@a.org',
                              'extra_weird_info': 'blah'})
    def test_authenticate_returns_user_on_success(self, u, a):
        backend = nw.WebmakerOAuth2Backend()
        user = backend.authenticate('validcode')
        self.assertEqual(user.username, 'foo')
        self.assertEqual(user.email, 'foo@a.org')
        a.assert_called_with('validcode')
        u.assert_called_with('tok')

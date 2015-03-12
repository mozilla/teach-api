import json
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django_browserid.base import MockVerifier, VerificationResult

from .. import views
from .. import webmaker

class FakeBrowserIDBackend(webmaker.WebmakerBrowserIDBackend):
    def __init__(self, email):
        super(FakeBrowserIDBackend, self).__init__()
        self.__fake_email = email

    def get_verifier(self):
        return MockVerifier(self.__fake_email)

@override_settings(CORS_API_PERSONA_ORIGINS=['http://example.org'],
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

    @override_settings(CORS_API_PERSONA_ORIGINS=['*'], DEBUG=True)
    def test_any_origin_allowed_when_debugging(self):
        req = self.factory.post('/', HTTP_ORIGIN='http://foo.com')
        response = self.view(req)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'assertion required')

    @override_settings(CORS_API_PERSONA_ORIGINS=['*'], DEBUG=False)
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
        self.assertRegexpMatches(response.json['token'], r'^[0-9a-f]+$')

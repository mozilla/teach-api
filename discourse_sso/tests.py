import urlparse
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User

from .views import pack_and_sign_payload, unpack_and_verify_payload

@override_settings(DISCOURSE_SSO_SECRET='test',
                   DISCOURSE_SSO_ORIGIN='http://discourse.org')
class EndpointTests(TestCase):
    def login(self):
        self.user = User.objects.create_user('foo', 'foo@example.org', 'pass')
        self.assertTrue(self.client.login(username='foo',
                                          password='pass'))

    def test_invalid_payloads_are_rejected(self):
        self.login()
        payload = pack_and_sign_payload({'nonce': '1'}, secret='INVALID')
        response = self.client.get('/discourse_sso/', payload)

        self.assertEqual(response.status_code, 400)

    def test_members_are_redirected_to_discourse(self):
        self.login()
        payload = pack_and_sign_payload({'nonce': '1'})
        response = self.client.get('/discourse_sso/', payload)

        self.assertEqual(response.status_code, 302)

        loc = urlparse.urlparse(response['location'])
        self.assertEqual(loc.scheme, 'http')
        self.assertEqual(loc.netloc, 'discourse.org')
        self.assertEqual(loc.path, '/session/sso_login')

        query_dict = dict(urlparse.parse_qsl(loc.query))
        self.assertEqual(unpack_and_verify_payload(query_dict), {
            'email': 'foo@example.org',
            'require_activation': 'true',
            'external_id': str(self.user.id),
            'name': 'foo',
            'nonce': '1',
            'username': 'foo'
        })

from base64 import b64encode
from django.core.exceptions import MiddlewareNotUsed
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from ..admin_protection import BasicAuthMiddleware

@override_settings(ADMIN_PROTECTION_USERPASS='foo:bar')
class BasicAuthMiddlewareEnabledTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mw = BasicAuthMiddleware()

    def test_non_admin_paths_are_unaffected(self):
        req = self.factory.get('/foo')
        self.assertEqual(self.mw.process_request(req), None)

    def test_admin_paths_return_401(self):
        req = self.factory.get('/admin/')
        res = self.mw.process_request(req)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res['WWW-Authenticate'], 'Basic realm="Admin"')

    def test_admin_paths_return_401_when_userpass_is_incorrect(self):
        userpass = b64encode('wrong:credentials')
        req = self.factory.get('/admin/',
                               HTTP_AUTHORIZATION='basic %s' % userpass)
        self.assertEqual(self.mw.process_request(req).status_code, 401)

    def test_admin_paths_return_401_when_userpass_is_not_base64(self):
        req = self.factory.get('/admin/',
                               HTTP_AUTHORIZATION='basic lol')
        self.assertEqual(self.mw.process_request(req).status_code, 401)

    def test_admin_paths_return_401_when_auth_is_not_basic(self):
        req = self.factory.get('/admin/',
                               HTTP_AUTHORIZATION='ridiculous lol')
        self.assertEqual(self.mw.process_request(req).status_code, 401)

    def test_admin_paths_passthrough_when_userpass_is_correct(self):
        userpass = b64encode('foo:bar')
        req = self.factory.get('/admin/',
                               HTTP_AUTHORIZATION='basic %s' % userpass)
        self.assertEqual(self.mw.process_request(req), None)

@override_settings(ADMIN_PROTECTION_USERPASS='')
class BasicAuthMiddlewareDisabledTests(TestCase):
    def test_constructor_raises_not_used_when_setting_is_falsy(self):
        self.assertRaises(
            MiddlewareNotUsed,
            BasicAuthMiddleware
        )

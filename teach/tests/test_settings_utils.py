import os
from django.test import TestCase
from mock import patch

from ..settings_utils import set_default_env, set_default_db, \
                             parse_email_backend_url, \
                             parse_secure_proxy_ssl_header

class SetDefaultEnvTests(TestCase):
    def test_sets_default_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            del os.environ['TEST_FOO']
            set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], 'bar')

    def test_does_not_overwrite_existing_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], '')

class SetDefaultDbTests(TestCase):
    def test_follows_env_vars(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'FOO', 'FOO': 'bar'}):
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'bar')

    def test_does_not_overwrite_existing_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'foo'}):
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'foo')

    def test_sets_default_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': ''}):
            del os.environ['DATABASE_URL']
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'meh')

class ParseEmailBackendUrlTests(TestCase):
    def test_accepts_console(self):
        self.assertEqual(parse_email_backend_url('console:'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
            'EMAIL_BACKEND_INSTALLED_APPS': ()
        })

    def test_accepts_mandrill(self):
        self.assertEqual(parse_email_backend_url('mandrill://lol'), {
            'EMAIL_BACKEND': 'djrill.mail.backends.djrill.DjrillBackend',
            'MANDRILL_API_KEY': 'lol',
            'EMAIL_BACKEND_INSTALLED_APPS': ('djrill',)
        })

    def test_accepts_smtp_without_auth(self):
        self.assertEqual(parse_email_backend_url('smtp://foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25,
            'EMAIL_BACKEND_INSTALLED_APPS': ()
        })

    def test_accepts_smtp_with_auth(self):
        self.assertEqual(parse_email_backend_url('smtp://a:b@foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25,
            'EMAIL_HOST_USER': 'a',
            'EMAIL_HOST_PASSWORD': 'b',
            'EMAIL_BACKEND_INSTALLED_APPS': ()
        })

    def test_accepts_smtp_plus_tls(self):
        self.assertEqual(parse_email_backend_url('smtp+tls://foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25,
            'EMAIL_BACKEND_INSTALLED_APPS': ()
        })

class ParseSecureProxySslHeaderTests(TestCase):
    def test_basic_functionality(self):
        self.assertEqual(
            parse_secure_proxy_ssl_header('X-Forwarded-Proto: https'),
            ('HTTP_X_FORWARDED_PROTO', 'https')
        )

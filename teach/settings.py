"""
Django settings for teach project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import sys
import urlparse
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path = lambda *parts: os.path.join(BASE_DIR, *parts)

from .settings_utils import set_default_env, set_default_db, \
                            parse_email_addresses, \
                            parse_email_backend_url, \
                            parse_secure_proxy_ssl_header, \
                            is_running_test_suite

if os.path.basename(sys.argv[0]) == 'manage.py' or 'DEBUG' in os.environ:
    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
    set_default_env(
        SECRET_KEY='development mode',
        DEBUG='indeed',
        # TODO: Support any alternative port passed-in from the command-line.
        PORT='8000',
        EMAIL_BACKEND_URL='console:',
        CORS_API_LOGIN_ORIGINS='*'
    )

CREDLY_API_URL = os.environ.get('CREDLY_API_URL', '.')
CREDLY_API_KEY = os.environ.get('CREDLY_API_KEY', 'missing')
CREDLY_APP_SECRET = os.environ.get('CREDLY_APP_SECRET', 'missing')
CREDLY_ACCOUNT_EMAIL = os.environ.get('CREDLY_ACCOUNT_EMAIL', 'missing@example.org')
CREDLY_ACCOUNT_PASSWORD = os.environ.get('CREDLY_ACCOUNT_PASSWORD', 'missing')
MozillaAccountId = os.environ.get('MozillaAccountId', -1)

IDAPI_URL = os.environ.get('IDAPI_URL', 'https://id.webmaker.org')
IDAPI_CLIENT_ID = os.environ.get('IDAPI_CLIENT_ID')
IDAPI_CLIENT_SECRET = os.environ.get('IDAPI_CLIENT_SECRET')

LOGINAPI_URL = os.environ.get('LOGINAPI_URL', 'https://login.webmaker.org')
LOGINAPI_AUTH = os.environ.get('LOGINAPI_AUTH')

TEACH_SITE_URL = os.environ.get('TEACH_SITE_URL', 'https://teach.mozilla.org')

DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET')
DISCOURSE_SSO_ORIGIN = os.environ.get('DISCOURSE_SSO_ORIGIN')

if 'ADMIN_PROTECTION_USERPASS' in os.environ:
    ADMIN_PROTECTION_USERPASS = os.environ['ADMIN_PROTECTION_USERPASS']

if 'SECURE_PROXY_SSL_HEADER' in os.environ:
    SECURE_PROXY_SSL_HEADER = parse_secure_proxy_ssl_header(
        os.environ['SECURE_PROXY_SSL_HEADER']
    )

if 'DEFAULT_FROM_EMAIL' in os.environ:
    DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = TEMPLATE_DEBUG = 'DEBUG' in os.environ

PORT = int(os.environ['PORT'])

if DEBUG: set_default_env(ORIGIN='http://localhost:%d' % PORT)

if DEBUG and IDAPI_URL.startswith('fake:'):
    IDAPI_ENABLE_FAKE_OAUTH2 = True
    IDAPI_FAKE_OAUTH2_USERNAME = IDAPI_URL.split(':')[1]
    IDAPI_FAKE_OAUTH2_EMAIL = IDAPI_URL.split(':')[2]
else:
    IDAPI_ENABLE_FAKE_OAUTH2 = False

set_default_db('sqlite:///%s' % path('db.sqlite3'))

globals().update(parse_email_backend_url(os.environ['EMAIL_BACKEND_URL']))

ORIGIN = os.environ['ORIGIN']

BROWSERID_AUDIENCES = [ORIGIN]
BROWSERID_AUTOLOGIN_ENABLED = False

if DEBUG and os.environ.get('BROWSERID_AUTOLOGIN_EMAIL'):
    BROWSERID_AUTOLOGIN_EMAIL = os.environ['BROWSERID_AUTOLOGIN_EMAIL']
    BROWSERID_AUTOLOGIN_ENABLED = True

TEACH_STAFF_EMAILS = parse_email_addresses(
    os.environ.get('TEACH_STAFF_EMAILS', '')
)

ALLOWED_HOSTS = [urlparse.urlparse(ORIGIN).hostname]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_browserid',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'clubs',
    'clubs_guides',
    'groups',
    'credly'
)

if IDAPI_ENABLE_FAKE_OAUTH2:
    INSTALLED_APPS += (
        'fake_oauth2',
    )

if DISCOURSE_SSO_SECRET or is_running_test_suite():
    INSTALLED_APPS += ('discourse_sso',)

MIDDLEWARE_CLASSES = ()

if not DEBUG:
    MIDDLEWARE_CLASSES += (
        'teach.ssl.RedirectToHttpsMiddleware',
        'teach.ssl.HstsMiddleware',
    )

MIDDLEWARE_CLASSES += (
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'teach.admin_protection.BasicAuthMiddleware',
    'teach.p3p.P3PMiddleware',
)

AUTHENTICATION_BACKENDS = ()

if BROWSERID_AUTOLOGIN_ENABLED:
    AUTHENTICATION_BACKENDS += ('django_browserid.auth.AutoLoginBackend',)

AUTHENTICATION_BACKENDS += (
   'django.contrib.auth.backends.ModelBackend',
   'teach.new_webmaker.WebmakerOAuth2Backend',
   'teach.webmaker.WebmakerBrowserIDBackend',
)

ROOT_URLCONF = 'teach.urls'

WSGI_APPLICATION = 'teach.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = path('staticfiles')

CSP_IMG_SRC = ("'self'", "data:")
CSP_SCRIPT_SRC = ("'self'", "https://login.persona.org")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_FRAME_SRC = ("'self'", "https://login.persona.org")

LOGIN_REDIRECT_URL = '/'

# TODO: Mail admins on error.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'teach.oauth2': {
            'handlers': ['console'],
            'level': 'WARNING'
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR'
        }
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # This is needed to use the self-documenting browser UI.
        'rest_framework.authentication.SessionAuthentication',
        # This is needed to access the API programattically.
        'rest_framework.authentication.TokenAuthentication'
    ]
}

STATICFILES_DIRS = (
    path('teach', 'static'),
)

TEMPLATE_DIRS = (
    path('teach', 'templates'),
)

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^(/api/).*$'

CORS_API_LOGIN_ORIGINS = os.environ.get(
    'CORS_API_LOGIN_ORIGINS',
    ''
).split(',')

LOGIN_URL = 'teach.views.oauth2_authorize'

if is_running_test_suite():
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

if not DEBUG:
    # Production deploys *must* be over HTTPS.
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

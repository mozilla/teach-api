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
    )

LOGINAPI_URL = os.environ.get('LOGINAPI_URL', 'https://login.webmaker.org')
LOGINAPI_AUTH = os.environ.get('LOGINAPI_AUTH')

if 'SECURE_PROXY_SSL_HEADER' in os.environ:
    SECURE_PROXY_SSL_HEADER = parse_secure_proxy_ssl_header(
        os.environ['SECURE_PROXY_SSL_HEADER']
    )


SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = TEMPLATE_DEBUG = 'DEBUG' in os.environ

PORT = int(os.environ['PORT'])

if DEBUG: set_default_env(ORIGIN='http://localhost:%d' % PORT)

set_default_db('sqlite:///%s' % path('db.sqlite3'))

ORIGIN = os.environ['ORIGIN']

BROWSERID_AUDIENCES = [ORIGIN]
BROWSERID_AUTOLOGIN_ENABLED = False

if DEBUG and os.environ.get('BROWSERID_AUTOLOGIN_EMAIL'):
    BROWSERID_AUTOLOGIN_EMAIL = os.environ['BROWSERID_AUTOLOGIN_EMAIL']
    BROWSERID_AUTOLOGIN_ENABLED = True

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
    'rest_framework',
    'rest_framework.authtoken',
    'example',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = ()

if BROWSERID_AUTOLOGIN_ENABLED:
    AUTHENTICATION_BACKENDS += ('django_browserid.auth.AutoLoginBackend',)

AUTHENTICATION_BACKENDS += (
   'django.contrib.auth.backends.ModelBackend',
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
    ]
}

if is_running_test_suite():
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

if not DEBUG:
    # Production deploys *must* be over HTTPS.
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

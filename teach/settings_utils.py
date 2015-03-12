import os
import sys
import urlparse

def set_default_env(**kwargs):
    for key in kwargs:
        if not key in os.environ:
            os.environ[key] = kwargs[key]

def set_default_db(default):
    set_default_env(DATABASE_URL=default)
    url = os.environ['DATABASE_URL']
    if url.upper() == url:
        # The environment variable is naming another environment variable,
        # whose value we should retrieve.
        os.environ['DATABASE_URL'] = os.environ[url]

def parse_email_backend_url(url):
    info = urlparse.urlparse(url)
    s = {'EMAIL_BACKEND_INSTALLED_APPS': ()}
    if info.scheme == 'console':
        s['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
    elif info.scheme in ['smtp', 'smtp+tls']:
        s['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
        s['EMAIL_HOST'] = info.hostname
        s['EMAIL_PORT'] = info.port
        if info.scheme == 'smtp+tls':
            s['EMAIL_USE_TLS'] = True
        if info.username:
            s['EMAIL_HOST_USER'] = info.username
        if info.password:
            s['EMAIL_HOST_PASSWORD'] = info.password
    elif info.scheme == 'mandrill':
        s['EMAIL_BACKEND'] = 'djrill.mail.backends.djrill.DjrillBackend'
        s['MANDRILL_API_KEY'] = info.netloc
        s['EMAIL_BACKEND_INSTALLED_APPS'] = ('djrill',)
    else:
        raise ValueError('unknown scheme for email backend url: %s' % url)
    return s

def parse_secure_proxy_ssl_header(field):
    name, value = field.split(':')
    return ('HTTP_%s' % name.upper().replace('-', '_'), value.strip())

def is_running_test_suite():
    return (os.path.basename(sys.argv[0]) == 'manage.py' and 
            len(sys.argv) > 1 and sys.argv[1] == 'test')

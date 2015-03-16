from django.test import TestCase, RequestFactory

from ..ssl import RedirectToHttpsMiddleware, HstsMiddleware

class SslTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_redirect_to_https_redirects_insecure_requests(self):
        request = self.factory.get('/foo', HTTP_HOST='example.org')
        mw = RedirectToHttpsMiddleware()
        response = mw.process_request(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], 'https://example.org/foo')

    def test_redirect_to_https_ignores_secure_requests(self):
        request = self.factory.get('/foo', HTTP_HOST='example.org')
        request.is_secure = lambda: True
        mw = RedirectToHttpsMiddleware()
        self.assertEqual(mw.process_request(request), None)

    def test_hsts_middleware_works(self):
        response = {}
        mw = HstsMiddleware()
        mw.process_response(None, response)
        self.assertEqual(response, {
            "Strict-Transport-Security": "max-age=31536000; " \
                                         "includeSubdomains"
        })

from django.test import TestCase

from ..p3p import P3PMiddleware

class P3PMiddlewareTests(TestCase):
    def test_header_is_added(self):
        response = {}
        mw = P3PMiddleware()
        response = mw.process_response(None, response)
        self.assertRegexpMatches(
            response['P3P'],
            r'^CP="This is not a P3P policy'
        )

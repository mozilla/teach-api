POLICY = ('CP="This is not a P3P policy, but Mozilla deeply cares about '
          'your privacy. See https://www.mozilla.org/en-US/privacy/websites/ '
          'for more."')

class P3PMiddleware(object):
    """
    Add 'P3P' headers so that IE, with default security settings, will allow
    us to set third-party cookies. For more information, see:

    https://github.com/mozilla/teach.webmaker.org/issues/727
    """

    def process_response(self, request, response):
        response['P3P'] = POLICY
        return response

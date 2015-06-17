import base64
import urlparse
import hmac
import urllib
from hashlib import sha256
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

if hasattr(hmac, 'compare_digest'):
    compare_digest = hmac.compare_digest
else:
    # Slightly modified from http://stackoverflow.com/a/18173992.
    def compare_digest(x, y):
        if not (isinstance(x, bytes) and isinstance(y, bytes)):
            raise TypeError("both inputs should be instances of bytes")
        if len(x) != len(y):
            return False
        result = 0
        for a, b in zip(x, y):
            result |= ord(a) ^ ord(b)
        return result == 0

def hmac_sign(payload, secret=None):
    if secret is None: secret = settings.DISCOURSE_SSO_SECRET
    return hmac.new(secret, payload, sha256)

def unpack_and_verify_payload(query_dict):
    payload = query_dict['sso']
    their_sig = query_dict['sig'].decode('hex')
    our_sig = hmac_sign(payload).digest()

    if not compare_digest(our_sig, their_sig):
        raise Exception('invalid signature')

    return dict(urlparse.parse_qsl(base64.b64decode(payload)))

def pack_and_sign_payload(payload_dict, secret=None):
    payload = base64.b64encode(urllib.urlencode(payload_dict))
    return {
        'sso': payload,
        'sig': hmac_sign(payload, secret).hexdigest()
    }

def user_info_qs(user, nonce):
    user_name = user.get_full_name() or user.username
    return urllib.urlencode(pack_and_sign_payload({
        'nonce': nonce,
        'require_activation': 'true',
        'email': str(user.email),
        'external_id': str(user.id),
        'username': str(user.username),
        'name': user_name.encode('utf8')
    }))

@login_required
def sso_endpoint(request):
    try:
        nonce = unpack_and_verify_payload(request.GET)['nonce']
    except Exception:
        return HttpResponseBadRequest()

    url = '%s/session/sso_login?%s' % (
        settings.DISCOURSE_SSO_ORIGIN,
        user_info_qs(request.user, nonce)
    )

    return HttpResponseRedirect(url)

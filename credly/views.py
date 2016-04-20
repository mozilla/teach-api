import base64
import json

from datetime import date, timedelta

import requests;
from requests.auth import AuthBase

import slumber
from slumber.exceptions import HttpClientError, HttpNotFoundError
from django.conf import settings

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from teach.settings import CREDLY_API_KEY, CREDLY_APP_SECRET, CREDLY_API_URL, CREDLY_ACCOUNT_EMAIL, CREDLY_ACCOUNT_PASSWORD, MozillaAccountId
from credly.models import UserCredlyProfile, create_new_user, save_user_token, get_credly_access_token, get_credly_token_age

# ------------------------------------------------------
# Auth handler to ensure headers/params for Credly calls
# ------------------------------------------------------

class ApiAuth(AuthBase):
    def __init__(self, api_key, api_secret, email=None, password=None):
        self.api_key = api_key
        self.api_secret = api_secret

        self.email = email
        self.password = password

    def __call__(self, r):
        r.headers['X-Api-Key'] = self.api_key
        r.headers['X-Api-Secret'] = self.api_secret

        if self.email and self.password:
            base64string = base64.encodestring('%s:%s' % (self.email, self.password))[:-1]
            auth_header = "Basic %s" % base64string
            r.headers['Authorization'] = auth_header

        #print r.headers
        return r


# ------------------------------------------------------
#             Requests helper definitions
# ------------------------------------------------------

def XAPIHeaders():
    return {
        'X-Api-Key': CREDLY_API_KEY,
        'X-Api-Secret': CREDLY_APP_SECRET
    }

def credlyAuth():
    return ApiAuth(
        CREDLY_API_KEY,
        CREDLY_APP_SECRET,
        email = CREDLY_ACCOUNT_EMAIL,
        password = CREDLY_ACCOUNT_PASSWORD
    )

def APICredentials():
    return {
        'email': CREDLY_ACCOUNT_EMAIL,
        'password': CREDLY_ACCOUNT_PASSWORD
    }

# ------------------------------------------------------
#               Route handling helpers
# ------------------------------------------------------

'''
  FIXME: TODO: this is repeated from teach/views.py -> refactor
'''
def check_origin(request):
    origin = request.META.get('HTTP_ORIGIN')
    valid_origins = settings.CORS_API_LOGIN_ORIGINS
    if not origin or origin not in valid_origins:
        if not (settings.DEBUG and valid_origins == ['*']):
            return None
    res = HttpResponse()
    res['access-control-allow-origin'] = origin
    return res

'''
  The browser may do a preflight check for XHR with payloads,
  so we use the require_http_methods decorator to indicate we
  will process OPTIONS and POST, and if we see the first, we
  respond with what is effectively a generic preflight response.
'''
def check_OPTIONS(request, res):
    if request.method == "OPTIONS":
        res['allow'] = 'post,options'
        res['Access-Control-Allow-Headers'] = 'Content-Type'
        return True
    return False

'''
  FIXME: TODO: this is repeated from teach/views.py -> refactor
'''
def json_response(res, data):
    res['content-type'] = 'application/json'
    res.content = json.dumps(data)
    return res


# ------------------------------------------------------
#               View-internal functions
# ------------------------------------------------------


'''
  Get a credly instance
'''
def get_credly(email=None, password=None):
    if email and password:
        return slumber.API(CREDLY_API_URL, auth=ApiAuth(CREDLY_API_KEY, CREDLY_APP_SECRET, email=email, password=password), append_slash=False)
    return slumber.API(CREDLY_API_URL, auth=ApiAuth(CREDLY_API_KEY, CREDLY_APP_SECRET), append_slash=False)

'''
  Get the Mozilla-authenticated credly instance
'''
def get_our_credly():
    return get_credly(email=CREDLY_ACCOUNT_EMAIL, password=CREDLY_ACCOUNT_PASSWORD)

'''
  Bootstrap a user instance and response object for an incoming request.
'''
def boostrap_no_credly(request):
    res = check_origin(request)
    res['access-control-allow-credentials'] = 'true'
    user = request.user
    return (res, user)

'''
  Bootstrap a user instance, response object, and credly instance for an incoming request.
'''
def bootstrap(request, email=False, password=False):
    (res, user) = boostrap_no_credly(request)
    credly = get_credly(email, password)
    return (res, user, credly)

'''
  Retrieve the user profile as stored by Django for the given user
'''
def check_local_profile(user_id):
    try:
        profile = get_object_or_404(UserCredlyProfile, user_id=user_id)
        return profile
    except Exception as error:
        return None

'''
  Get the Credly member information for a user, based on their stored access token
'''
def get_member_data(credly, user):
    access_token = get_access_token(user.id)
    list_result = credly.me.get(access_token=access_token)
    return list_result['data']

'''
  Get a user's stored Credly access token
'''
def get_access_token(user_id):
    profile = check_local_profile(user_id)
    if not profile:
        return None
    return profile.access_token;

'''
  Get the Mozilla Credly access token for administrative Credly calls
'''
def get_our_access_token():
    headers = XAPIHeaders()
    auth = credlyAuth()
    data = APICredentials()
    url = CREDLY_API_URL + 'authenticate'
    try:
        result = requests.post(url, headers=headers, auth=auth, data=data)
        response = json.loads(result.text)
        token = response['data']
        return token['token']
    except HttpNotFoundError as error:
        print error
        return None

'''
  Ensure that the credly user table has an entry for this id.wmo user.
'''
def ensure_user(user):
    profile = check_local_profile(user.id)
    if not profile:
        print "user does not have a UserCredlyProfile, making new profile"
        create_new_user(user.id)

'''
  Request a credly access_token for an id.wmo user. This may do several things:

  - if the user is an id.wmo user only, and the user provided us with
    credentials for use with Credly, we either:

    - link their Credly account to their id.wmo account through an access_token
      (we do not store their Credly credentials).

    - create a new Credly account that gets linked to their id.wmo account through
      and access_token (again, we do not store their Credly credentials);

  - if the user is an id.wmo user with an associated Credly access_token, we:

    - use the stored token if it's "fresh" enough

    - we refresh the token if it's close to expiring

    - we notify the caller that this user's token has expired and requires
      the user to provide us with the credly credentials again, so that we
      can negotiate a new access_token for them.
'''
def request_credly_token(user, email=None, password=None):
    token = None
    profile = check_local_profile(user.id)
    credly = get_credly(email, password)
    token_age = get_credly_token_age(user.id)

    # no acccess_token was ever set, so set one up.
    if not token_age:
        print "this user was never linked to Credly before. Linking..."
        moz_credly = get_our_credly()
        moz_token = get_our_access_token()
        try:
            is_member = moz_credly.members().get(email=email, access_token=moz_credly)
            # if we've not hit an exception, this is a known credly user and we should
            # be able to get an access and refresh token associated with their account.
            result = credly.authenticate.post()
            token = result['data']
            print "Linked teach-api user to Credly."
            save_user_token(user.id, token)
        except HttpNotFoundError as not_found_error:
            print "No Credly account found for the supplied email, creating a new account..."
            # not a known credly user, we'll have to register them
            try:
                headers = XAPIHeaders()
                params = { 'access_token': moz_token }
                data = { 'email': email, 'password': password, 'is_email_verified': 1 }
                url = CREDLY_API_URL + 'authenticate/register'
                result = requests.post(url, params=params, headers=headers, data=data)
                response = json.loads(result.text)
                token = response['data']
                print "Created new Credly account for teach-api user."
                save_user_token(user.id, token)
            except HttpClientError as clienterror:
                print clienterror
                pass
            pass

    # access_token is still good
    elif token_age < 80:
        print "access token is still valid, using directly"
        token = { 'token': profile.access_token, 'refresh_token': profile.refresh_token }

    # access token expired, user will have to reauthenticate with their password
    elif token_age > 90:
        #
        # FIXME:TODO: THIS SHOULD BE A CRON JOB OF SOME SORT BUT CAN LIVE HERE FOR NOW.
        #
        print "a new access token needs to be requested"
        result = credly.authenticate.post()
        token = result['data']
        save_user_token(user.id, token)

    # refresh the access_token
    else:
        print "access token requires a refresh"
        result = credly.authenticate.refresh.post({ 'refresh_token': profile.refresh_token })
        token = result['data']
        save_user_token(user.id, token)

    return token

'''
  Get a user's list of badges earned through Credly.

  Credly is adding "show_earned" to an issuer's badge list,
  when requested via an API call that is authenticated for a
  specific user, which should provide us with more targetted
  information relevant only to our own-issued badges. (We do
  not really want a million user badges, we really just want
  the list of "our" badges that they have earned)
'''
def get_user_badges(credly, user):
    user_data = get_member_data(credly, user)
    user_result = credly.members(user_data['id']).badges.get()
    return user_result['data']

'''
  Get the list of pending badge requests from the Mozilla inbox.

  We use this to cross reference "earned" badges, as Credly badges
  do not strictly have a "pending" status, and so the only good way
  to figure out if they're pending is to get the list of earned
  badges for a user, and then cross-reference that with our pending
  request inbox.

  Credly may be adding "show_pending" to an issuer's badge list
  when requested via an API call that is authenticated for a specific
  user, which would obviate the need for this this function.
'''
def get_pending_badges():
    credly = get_our_credly()
    access_token = get_our_access_token()
    list_result = credly.me.claimable_badges.pending.get(access_token=access_token)
    return list_result['data']

'''
  Get a specific badge from our set of Mozilla badges.

  Note that this function is not currently used, as we need
  prev/next information for badges, which the Credly API does
  not supply. As such, we retrieve the full badge list instead
  and then filter out the requested badge and its siblings,
  rather than using this function.
'''
def get_mozilla_badge(credly, badge_id):
    badge_result = credly.badges(badge_id).get()
    return badge_result['data']

'''
  Get all Mozilla badges that we issue through Credly.
  If no access_token is available, meaning we do not have
  an authenticated user that may require cross-referencing
  data, we request the list "as Mozilla", without the
  additional information provided via the "verbose" and
  "show_earned" flags.
'''
def get_mozilla_badges(credly=None, access_token=None):
    verbose = 1
    show_earned = 1
    if not access_token:
        credly = get_our_credly()
        access_token = get_our_access_token()
        verbose = 0
        show_earned = 0
    list_result = credly.members(MozillaAccountId).badges.created.get(verbose=1, show_earned=1, access_token=access_token)
    return list_result['data']


# ------------------------------------------------------
#                API endpoints
# ------------------------------------------------------


'''
  API GET endpoint for checking whether the current session's
  id.wmo user has Credly access or not. This check is based
  on whether there a stored Credly access_token in our database.
'''
@require_GET
def has_access(request):
    (res, user) = boostrap_no_credly(request)

    data = { 'access': False }

    # no user session means we have nothing to check
    if not user:
        return json_response(res, data)

    # no credly token means the user needs to credly-login
    if not get_access_token(user.id):
        return json_response(res, data)

    # we have credly access for the user.
    data['access'] = True
    return json_response(res, data)

'''
  API POST endpoint for making sure that the current
  session's id.wmo user is linked to credly, with access_token
  valid credly access token.
'''
@require_http_methods(["POST", "OPTIONS"])
@csrf_exempt
def ensure_login(request):
    (res, user, credly) = bootstrap(request)

    # perform preflight clearance
    if check_OPTIONS(request, res):
        return res

    # get the user's
    formData = None
    if request.body:
        formData = json.loads(request.body);

    if formData is None:
        return json_response(res, {
            'result': 'failed',
            'reason': 'missing post data'
        })

    # build a user record in the credly table
    ensure_user(user)

    # negotiate a credly access token for this user
    email = formData['email']
    password = formData['password']
    token = request_credly_token(user, email, password)

    if token is False:
        return json_response(res, {
            'result': 'failed',
            'reason': 'missing token'
        })

    return json_response(res, {
        'result': 'obtained new access and refresh tokens'
    })

'''
  API GET enpoind for getting the list of Mozilla badges
  crosslinked to this session's user's list of earned
  badges and the Mozilla inbox for badge requests, so that
  we can show badges as having been achieved, are pending
  approval, or are still elligible for earning.
'''
@require_GET
def badgelist(request):
    (res, user, credly) = bootstrap(request)

    #
    # NOTE: THIS FUNCTION DOES A LOT OF API CALLS, AND WE
    #       NEED TO FIND A WAY TO SPEED THAT UP. ESPECIALLY
    #       THE "PENDING REQUESTS" TAKES FOREVER.
    #

    # get the mozilla badges
    access_token = get_access_token(user.id);

    moz_badges = get_mozilla_badges(credly, access_token)
    moz_badge_ids = [n['id'] for n in moz_badges]

    if not hasattr(user, 'email') or not access_token:
        return json_response(res, {
            'badges': moz_badges
        })

    # shortlist the earned badges by this user
    earned_ids = [n['id'] for n in moz_badges if not n['member_badge_id'] == None]

    # get the user's pending badges
    pending_ids = []
    moz_pending = get_pending_badges()
    if not moz_pending == None:
      user_data = get_member_data(credly, user)
      pending_ids = [n['badge_id'] for n in moz_pending if n['member_id'] == user_data['id']]

    return json_response(res, {
        'username': user.username,
        'badges': moz_badges,
        'earned': earned_ids,
        'pending': pending_ids
    })

'''
  API GET endpoint for retrieving a single badge.
  Rather than actually retrieving one badge, we send
  back the requested badge and its immediate siblings
  (with under/overflow rollover so that all badges have
  'previous' and 'next' siblings), for badge navigation
  purposes.
'''
@require_GET
def badge(request, badge_id):
    (res, user, credly) = bootstrap(request)

    # get the mozilla badges
    access_token = get_access_token(user.id)
    all_badges = get_mozilla_badges(credly, access_token)

    # find "this" badge in that list, as well as its siblings
    badge_count = len(all_badges)
    index = 0
    for index, item in enumerate(all_badges):
        if item['id'] == int(badge_id):
            break
    else:
        index = -1

    # 'previous' (with underflow roll) sibling
    prev = False
    if index > 0:
        prev = all_badges[index-1]
    else:
        prev = all_badges[badge_count-1]

    # 'next' (with overflow roll) sibling
    next = False
    if index < badge_count-1:
        next = all_badges[index+1]
    else:
        next = all_badges[0]

    # 'this' badge
    single_badge = all_badges[index]

    if not access_token:
        return json_response(res, {
            'badge': single_badge,
            'prev': prev,
            'next': next
        })

    # if the user is fully signed in, get their list of earned badges
    #
    # FIXME: TODO: there is now a show_earned that _should_ remove the need for this call?
    #
    user_badges = get_user_badges(credly, user)
    user_badge_ids = []
    if user_badges:
      user_badge_ids = [n['badge_id'] for n in user_badges]
    earned = int(badge_id) in user_badge_ids

    # get the user's pending badges
    pending = False
    moz_pending = get_pending_badges()
    if not moz_pending == None:
      user_data = get_member_data(credly, user)
      pending_ids = [n['badge_id'] for n in moz_pending if n['member_id'] == user_data['id']]
      pending = int(badge_id) in pending_ids

    return json_response(res, {
        'username': user.username,
        'badge': single_badge,
        'earned': earned,
        'pending': pending,
        'prev': prev,
        'next': next
    })

'''
  API POST endpoint for claiming one of our Mozilla badges
  on behalf of the logged-in id.wmo user.

  Claims can be accompanied by evidence, which can take the
  form of a textual explanation, a URL, and a file attachment.
  Technically there is no limit on this evidence, but the
  Credly API rejects claims with files over 20MB. This does
  not feel like something we realistically _need_ to check
  for, so for now we don't.
'''
@require_http_methods(["POST", "OPTIONS"])
@csrf_exempt
def claim_badge(request, badge_id):
    (res, user, credly) = bootstrap(request)

    # perform preflight clearance
    if check_OPTIONS(request, res):
        return res

    # if we get here, we're dealing with an actual POST operation.
    formData = { 'evidences': [] }
    if request.body:
        formData = json.loads(request.body);

    result = False
    evidences = formData['evidences']
    access_token = get_credly_access_token(user.id);

    # We use requests here, due to the need for custom headers,
    # and URL parameters _and_ form data. This is a little more
    # than slumber wants to let you do.
    try:
        # Requests.post does not encode the data the way Credly expects
        # it, so we do a custom transform:
        evidencePayload = []
        for i, evidence in enumerate(evidences):
            arg = 'evidences[' + str(i) + '][file]=' + evidence['file']
            evidencePayload.append(arg)
            if not evidence['name'] == None:
                arg = 'evidences[' + str(i) + '][name]=' + evidence['name']
                evidencePayload.append(arg)
        data = "&".join(evidencePayload)
        headers = XAPIHeaders()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        params = { 'access_token': access_token }
        url = CREDLY_API_URL + 'me/claimable_badges/claim/' + badge_id
        result = requests.post(url, params=params, headers=headers, data=data)

    except HttpClientError as error:
        print error
        pass

    return json_response(res, {
        'result': result.text
    })

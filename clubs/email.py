CREATE_MAIL_SUBJECT = 'Thanks for joining the global movement to teach the web!'

CREATE_MAIL_BODY = """\
%(username)s,

Thanks for your interest in teaching the web! We are thrilled that you have taken the first step in your journey to becoming a Mozilla Club Captain.

Once your application is approved, a member of our team will get in touch with you to confirm that your club has been approved.

If you have any questions you can send an email to teachtheweb@mozillafoundation.org, tweet @MozLearn or using hashtag #teachtheweb.

Mozilla Clubs team
"""

CREATE_MAIL_STAFF_SUBJECT = 'Please review: new club has been submitted'

CREATE_MAIL_STAFF_BODY = """\
%(username)s would like to add their Club to the map.

Name: %(club_name)s
Location: %(club_location)s
Website: %(club_website)s
Description: %(club_description)s
Email: %(email)s

This club is currently in a pending state and you can approve or deny it
for inclusion in the public map at:

%(admin_url)s

You may also want to email them at %(email)s to say hello!
"""

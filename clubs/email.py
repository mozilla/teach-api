CREATE_MAIL_SUBJECT = 'Thanks for joining the global movement to teach the web!'

CREATE_MAIL_BODY = """\
%(username)s,

You did it! You put your city on the map and showed your dedication to increasing web literacy around the world. This is a big first step, so thank you for all that you are doing to teach the web.

Whether you are a new club leader or an expert at running clubs, we recommend you get started by meeting others in our community. Join the conversation in our discussion forum [http://discourse.webmaker.org/category/clubs], or tell us what you're teaching on Twitter using hashtag #teachtheweb.

A member of our team will send you an email soon to see how you're doing and make sure your club is on the road to success!

Michelle Thorne,
on behalf of the Mozilla Learning team

P.S. Be sure to check out our tips for running clubs at %(TEACH_SITE_URL)s/clubs/ !
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

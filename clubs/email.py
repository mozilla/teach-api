CREATE_MAIL_SUBJECT = 'Thanks for joining the global movement to teach the web!'

CREATE_MAIL_BODY = """\
%(username)s,

Thanks for your interest in teaching the web!

Get started right away by guiding a group of learners through these featured activities: %(TEACH_SITE_URL)s/activities/

We believe in the power of peer learning. That's why we match each Mozilla Club Captain with a volunteer Regional Coordinator who can support you in getting started and making the most of this program.

Please note: Our first cohort of Regional Coordinators is in full swing right now, so you've been added to our waiting list. We'll match you with a Regional Coordinator as soon as we can. Your club will not show up on the map until you've been matched up.

To begin on your own, check out these resources to organize and teach your learners: http://mozilla.github.io/learning-networks/clubs/#resources

Please also say hello in our discussion forum (http://discourse.webmaker.org/category/clubs) or tweet using hashtag #teachtheweb if you need any help.

Let's teach the web!

Michelle Thorne
on behalf of the Mozilla Learning Network
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

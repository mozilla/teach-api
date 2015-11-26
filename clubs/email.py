CREATE_MAIL_SUBJECT = 'Thanks for joining the global movement to teach the web!'

CREATE_MAIL_BODY = """\
%(username)s,

Thanks for your interest in teaching the web! We are thrilled that you have taken the first step in your journey to becoming a Mozilla Club Captain.

In order to better understand your plans and needs for your club, we'd like to know more about you. Please provide brief answers (2-3 sentences) to the questions in this survey http://bit.ly/1MP9BzB. Your answers will help us in the process of reviewing/approving your submission on the Mozilla Clubs map. Note, it is mandatory to complete and return these questions in order to proceed to the next step.

We look forward to hearing from you! You can tweet to us @mozteach or using hashtag #teachtheweb if you need any help.

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

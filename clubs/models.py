from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

class Club(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied')
    )

    NOT_INTERESTED = 'no longer interested'
    UNQUALIFIED = 'not qualified'
    NO_RESPONSE = 'no response'
    BAD_EMAIL = 'cannot be emailed'

    DENIAL_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (NOT_INTERESTED, 'No longer interested'),
        (UNQUALIFIED, 'Not qualified'),
        (NO_RESPONSE, 'No response after initial application'),
        (BAD_EMAIL, 'Applicant cannot be emailed')
    )

    teach_staff_permissions = ('add', 'change')
    regional_coordinator_permissions = ('change',)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    '''
        "Page 1" general values
    '''

    owner = models.ForeignKey(
        User,
        help_text="The user who owns the Club and can change it."
    )

    full_name = models.CharField(
        help_text="Full name for the Club captain for this club.",
        blank=False,
        null=True,
        max_length=200
    )

    location = models.CharField(
        help_text="Location of the club (city or country).",
        max_length=100
    )

    latitude = models.FloatField(
        help_text=("Latitude of the club. "
                   "Leave blank to automatically determine."),
        blank=True,
        null=True
    )

    longitude = models.FloatField(
        help_text=("Longitude of the club. "
                   "Leave blank to automatically determine."),
        blank=True,
        null=True
    )

    occupation = models.CharField(
        help_text=("Club captain's occupation."),
        blank=False,
        null=True,
        max_length=500
    )

    regional_coordinator = models.CharField(
        help_text=("Regional Coordinator associated with club captain."),
        blank=True,
        null=True,
        max_length=500
    )

    hosting_reason = models.TextField(
        help_text=("Reason to host a Mozilla club."),
        blank=False,
        null=True
    )

    how_they_heard = models.CharField(
        help_text="How did the applicant hear about Current approval status of the club.",
        blank=False,
        null=True,
        max_length=100
    )


    '''
        "Page 2" club-specific values
    '''

    intent = models.CharField(
        help_text="Is this for starting a new club or connecting an existing club?",
        max_length=100,
        default="start"
    )

    name = models.CharField(
        help_text="The name of the club.",
        max_length=100
    )

    description = models.TextField(
        help_text="Description of the club.",
        blank=False,
        null=False
    )

    venue = models.CharField(
        help_text="Where does this club meet.",
        blank=False,
        null=True,
        max_length=1000
    )

    # this is a range, and possibly "other" as user-supplied
    # information. As such, this is a text field.
    frequency = models.CharField(
        help_text=("How frequently this club meets."),
        blank=False,
        null=True,
        max_length=500
    )

    age_range = models.CharField(
        help_text=("The club member age range."),
        blank=False,
        null=True,
        max_length=500
    )

    club_size = models.CharField(
        help_text=("The number of club members."),
        blank=False,
        null=True,
        max_length=500
    )

    member_occupation = models.CharField(
        help_text=("Club member occupations."),
        blank=False,
        null=True,
        max_length=1000
    )

    club_topics = models.CharField(
        help_text=("Club topics/subjects."),
        blank=False,
        null=True,
        max_length=1000
    )

    '''
      Optional application values
    '''

    affiliation = models.CharField(
        help_text="The affiliated institution or organization.",
        blank=True,
        null=True,
        max_length=1000
    )

    website = models.URLField(
        help_text="The URL of the club's primary website.",
        blank=True,
        null=True,
        max_length=500
    )

    '''
      Administrative values
    '''

    status = models.CharField(
        help_text="Current approval status of the club.",
        max_length=10,
        choices=STATUS_CHOICES,
        default=APPROVED
    )

    denial = models.CharField(
        help_text="Reason for denial, if denied.",
        max_length=50,
        choices=DENIAL_CHOICES,
        default=PENDING
    )

    is_active = models.BooleanField(
        help_text="Designates whether this club should be treated "
                  "as active. Unselect this instead of deleting "
                  "clubs.",
        default=True
    )

    def __unicode__(self):
        return self.name

    def geocode(self, geolocator=None):
        if geolocator is None:
            geolocator = Nominatim()
        loc = geolocator.geocode(self.location)
        if loc is not None:
            self.latitude = loc.latitude
            self.longitude = loc.longitude

    def save(self, *args, **kwargs):
        geolocator = None
        if 'geolocator' in kwargs:
            geolocator = kwargs['geolocator']
            del kwargs['geolocator']
        if (self.location and
            self.latitude is None and
            self.longitude is None):
            try:
                self.geocode(geolocator)
            except Exception:
                pass

        super(Club, self).save(*args, **kwargs)

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

    teach_staff_permissions = ('add', 'change')
    regional_coordinator_permissions = ('change',)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        User,
        help_text="The user who owns the Club and can change it."
    )

    name = models.CharField(
        help_text="The name of the club.",
        max_length=100
    )

    website = models.URLField(
        help_text="The URL of the club's primary website.",
        blank=True
    )

    description = models.TextField(
        help_text="Description of the club."
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

    status = models.CharField(
        help_text="Current approval status of the club.",
        max_length=10,
        choices=STATUS_CHOICES,
        default=APPROVED
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

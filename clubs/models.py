from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

class Club(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(
        User,
        help_text="The user who created the Club."
    )

    name = models.CharField(
        help_text="The name of the club.",
        max_length=100
    )

    website = models.URLField(
        help_text="The URL of the club's primary website."
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
        help_text=("Longitude of the club."
                   "Leave blank to automatically determine."),
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        help_text="Designates whether this club should be treated "
                  "as active. Unselect this instead of deleting "
                  "clubs.",
        default=True
    )

    def geocode(self, geolocator=None):
        if geolocator is None:
            geolocator = Nominatim()
        loc = geolocator.geocode(self.location)
        if loc is not None:
            self.latitude = loc.latitude
            self.longitude = loc.longitude

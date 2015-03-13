from django.db import models
from geopy.geocoders import Nominatim

class Club(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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
        help_text="Latitude of the club."
    )

    longitude = models.FloatField(
        help_text="Longitude of the club."
    )

    is_active = models.BooleanField(
        help_text="Designates whether this club should be treated "
                  "as active. Unselect this instead of deleting "
                  "clubs.",
        default=True
    )

    def geocode(self):
        geolocator = Nominatim()
        loc = geolocator.geocode(self.location)
        if loc is not None:
            self.latitude = loc.latitude
            self.longitude = loc.longitude

from django.test import TestCase
from ..models import Club

import mock

class ClubTests(TestCase):
    def test_geocoding_sets_latlong(self):
        c = Club(location="foo")
        geolocator = mock.Mock()
        loc = mock.Mock()
        geolocator.geocode.return_value = loc
        loc.latitude = 2
        loc.longitude = 1
        c.geocode(geolocator)
        self.assertEqual(c.latitude, 2)
        self.assertEqual(c.longitude, 1)

    def test_geocoding_does_not_set_latlong(self):
        c = Club(location="foo", latitude=5,
                 longitude=6)
        geolocator = mock.Mock()
        loc = mock.Mock()
        geolocator.geocode.return_value = None
        c.geocode(geolocator)
        self.assertEqual(c.latitude, 5)
        self.assertEqual(c.longitude, 6)

from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Club

import mock

def mock_geolocator(latitude=None, longitude=None):
    geolocator = mock.Mock()
    if latitude is None or longitude is None:
        geolocator.geocode.return_value = None
    else:
        loc = mock.Mock()
        loc.latitude = latitude
        loc.longitude = longitude
        geolocator.geocode.return_value = loc
    return geolocator

class ClubTests(TestCase):
    def test_stringify_works(self):
        c = Club(name='Bop')
        self.assertEqual(str(c), 'Bop')

class ClubSaveTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@example.org')
        self.club = Club(location="foo", owner=self.user)

    def test_sets_latlong_when_they_are_not_yet_set(self):
        self.club.save(geolocator=mock_geolocator(2, 1))
        self.assertEqual(self.club.latitude, 2)
        self.assertEqual(self.club.longitude, 1)

    def test_does_not_set_latlong_when_they_are_already_set(self):
        self.club.latitude = 5
        self.club.longitude = 6
        self.club.save(geolocator=mock_geolocator(2, 1))
        self.assertEqual(self.club.latitude, 5)
        self.assertEqual(self.club.longitude, 6)

    def test_ignores_exceptions_from_geocoder(self):
        geo = mock.Mock()
        geo.geocode.side_effect=Exception('kaboom')
        self.club.save(geolocator=geo)
        self.assertEqual(self.club.latitude, None)
        self.assertEqual(self.club.longitude, None)

class ClubGeocodeTests(TestCase):
    def test_sets_latlong_when_geocoding_data_is_available(self):
        c = Club(location="foo")
        c.geocode(mock_geolocator(2, 1))
        self.assertEqual(c.latitude, 2)
        self.assertEqual(c.longitude, 1)

    def test_does_not_set_latlong_when_no_geocoding_data_is_available(self):
        c = Club(location="foo", latitude=5, longitude=6)
        c.geocode(mock_geolocator(None))
        self.assertEqual(c.latitude, 5)
        self.assertEqual(c.longitude, 6)

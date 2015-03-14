from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from ..models import Club
from ..views import ClubViewSet

class ClubViewSetTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1')
        self.user2 = User.objects.create_user('user2')
        self.client = APIClient()

        club = Club(
            owner=self.user1,
            name='my club',
            website='http://myclub.org/',
            description='This is my club.',
            location='Somewhere',
            latitude=5,
            longitude=6
        )
        club.save()
        self.club = club

    def test_list_clubs_works(self):
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{
            'url': 'http://testserver/api/clubs/1/',
            'name': 'my club',
            'website': 'http://myclub.org/',
            'description': 'This is my club.',
            'location': 'Somewhere',
            'latitude': 5,
            'longitude': 6
        }])

    def test_create_clubs_sets_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/clubs/', {
            'name': 'my club2',
            'website': 'http://myclub2.org/',
            'description': 'This is my club2.',
            'location': 'Somewhere else',
            'latitude': 1,
            'longitude': 2
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['url'],
                         'http://testserver/api/clubs/2/')
        self.assertEqual(Club.objects.get(pk=2).owner, self.user2)

    def test_list_clubs_only_shows_active_clubs(self):
        self.club.is_active = False
        self.club.save()
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_patch_clubs_without_auth_fails(self):
        response = self.client.patch('/api/clubs/1/', {'name': 'u'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Club.objects.get(pk=1).name, 'my club')

    def test_patch_clubs_with_auth_from_non_owner_fails(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch('/api/clubs/1/', {'name': 'u'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Club.objects.get(pk=1).name, 'my club')

    def test_patch_clubs_with_auth_from_owner_works(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch('/api/clubs/1/', {'name': 'u'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Club.objects.get(pk=1).name, 'u')

    def test_delete_clubs_marks_as_inactive(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete('/api/clubs/1/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Club.objects.get(pk=1).is_active)

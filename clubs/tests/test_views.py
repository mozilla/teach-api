from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings
from rest_framework.test import APIClient

from ..models import Club
from ..views import ClubViewSet

class ClubTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1')
        self.user2 = User.objects.create_user('user2', 'user2@example.org')
        self.client = APIClient()

        club = Club(
            owner=self.user1,
            name='my club',
            website='http://myclub.org/',
            description='This is my club.',
            location='Somewhere',
            latitude=5,
            longitude=6,
            status='approved'
        )
        club.save()
        self.club = club

class ClubViewSetTests(ClubTestCase):
    def test_list_clubs_works(self):
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{
            'url': 'http://testserver/api/clubs/1/',
            'owner': 'user1',
            'name': 'my club',
            'website': 'http://myclub.org/',
            'description': 'This is my club.',
            'location': 'Somewhere',
            'latitude': 5,
            'longitude': 6,
            'status': 'approved'
        }])

    def create_club(self):
        self.client.force_authenticate(user=self.user2)
        return self.client.post('/api/clubs/', {
            'name': 'my club2',
            'website': 'http://myclub2.org/',
            'description': 'This is my club2.',
            'location': 'Somewhere else',
            'latitude': 1,
            'longitude': 2
        })

    def test_create_clubs_sets_status_to_pending(self):
        response = self.create_club()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

    def test_update_clubs_changes_status_from_denied_to_pending(self):
        self.club.status = 'denied'
        self.club.save()
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch('/api/clubs/1/', {'description': 'u'})
        self.assertEqual(response.data['status'], 'pending')

    def test_update_clubs_does_not_change_status_if_already_approved(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch('/api/clubs/1/', {'description': 'u'})
        self.assertEqual(response.data['status'], 'approved')

    def test_update_clubs_does_not_change_status_if_already_pending(self):
        self.club.status = 'pending'
        self.club.save()
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch('/api/clubs/1/', {'description': 'u'})
        self.assertEqual(response.data['status'], 'pending')

    def test_create_clubs_sets_owner(self):
        response = self.create_club()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['url'],
                         'http://testserver/api/clubs/2/')
        self.assertEqual(Club.objects.get(pk=2).owner, self.user2)

    def test_create_clubs_sends_email_to_creator(self):
        response = self.create_club()
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ['user2@example.org'])
        self.assertRegexpMatches(msg.body, 'user2')

    @override_settings(TEACH_STAFF_EMAILS=['foo@bar.org'],
                       ORIGIN='https://s')
    def test_create_clubs_sends_email_to_teach_staff(self):
        response = self.create_club()
        msg = mail.outbox[1]
        self.assertEqual(msg.to, ['foo@bar.org'])
        self.assertRegexpMatches(msg.body, 'user2@example.org')
        self.assertRegexpMatches(msg.body, 'https://s/admin/clubs/club/2/')

    def test_list_clubs_only_shows_active_clubs(self):
        self.club.is_active = False
        self.club.save()
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_clubs_only_shows_approved_clubs_for_anonymous_users(self):
        self.club.status = 'pending'
        self.club.save()
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_clubs_hides_non_approved_clubs_of_other_users(self):
        self.club.status = 'pending'
        self.club.save()
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_clubs_shows_non_approved_clubs_of_logged_in_user(self):
        self.club.status = 'pending'
        self.club.save()
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

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

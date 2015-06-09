from django.test import TestCase
from django.test.utils import override_settings

from .test_views import ClubTestCase
from ..models import Club
from .. import admin

@override_settings(ORIGIN='https://s')
class ClubAdminTests(ClubTestCase):
    def test_export_csv_works(self):
        queryset = Club.objects.all()
        response = admin.export_csv(None, None, queryset)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=clubs.csv')
        self.assertEqual(response.content.splitlines(), [
            '\xef\xbb\xbfName,Location,Email,Description,Admin URL',
            'my club,Somewhere,,This is my club.,https://s/admin/clubs/club/1/'
        ])

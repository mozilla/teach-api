from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from .admin import site as teach_admin
teach_admin.copy_registry(admin.site)

from .views import TeachRouter
from clubs.views import ClubViewSet

router = TeachRouter()
router.register(r'clubs', ClubViewSet)

urlpatterns = [
    url(r'^auth/persona$', 'teach.views.persona_assertion_to_api_token'),
    url(r'^auth/status$', 'teach.views.get_status'),
    url(r'^auth/logout$', 'teach.views.logout'),

    url(r'^auth/oauth2/authorize$', 'teach.views.oauth2_authorize'),
    url(r'^auth/oauth2/callback$',  'teach.views.oauth2_callback'),
    url(r'^auth/oauth2/logout$',    'teach.views.oauth2_logout'),

    url(r'^api-introduction/', 'teach.views.api_introduction', name='api-introduction'),
    url(r'^api/', include(router.urls)),
    url(r'^$', RedirectView.as_view(url='/api/', permanent=False)),
    url(r'', include('django_browserid.urls')),
    url(r'^admin/', include(teach_admin.urls)),

    url(r'^credly/', include('credly.urls')),
    url(r'^api/clubsguides/', include('clubs_guides.urls')),
]

if settings.IDAPI_ENABLE_FAKE_OAUTH2:
    urlpatterns += [
        url(r'^fake_oauth2/', include('fake_oauth2.urls'))
    ]

if 'discourse_sso' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^discourse_sso/', include('discourse_sso.urls'))
    ]

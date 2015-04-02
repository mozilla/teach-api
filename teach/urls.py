from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

from .admin import site as teach_admin
teach_admin.copy_registry(admin.site)

from .views import TeachRouter
from clubs.views import ClubViewSet

router = TeachRouter()
router.register(r'clubs', ClubViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'teach.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # We intentionally don't want these under /api/, as they
    # have a different CORS policy than the rest of the API.
    url(r'^auth/persona$',
        'teach.views.persona_assertion_to_api_token'),
    url(r'^auth/status$',
        'teach.views.get_status'),
    url(r'^auth/logout$',
        'teach.views.logout'),

    url(r'^api-introduction/', 'teach.views.api_introduction',
        name='api-introduction'),
    url(r'^api/', include(router.urls)),
    url(r'^$', RedirectView.as_view(url='/api/')),
    url(r'', include('django_browserid.urls')),
    url(r'^admin/', include(teach_admin.urls)),
)

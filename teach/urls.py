from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework import routers

from .admin import site as teach_admin
teach_admin.copy_registry(admin.site)

from clubs.views import ClubViewSet

router = routers.DefaultRouter()
router.register(r'clubs', ClubViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'teach.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/auth/persona$',
        'teach.views.persona_assertion_to_api_token'),
    url(r'^api/', include(router.urls)),
    url(r'^$', RedirectView.as_view(url='/api/')),
    url(r'', include('django_browserid.urls')),
    url(r'^admin/', include(teach_admin.urls)),
)

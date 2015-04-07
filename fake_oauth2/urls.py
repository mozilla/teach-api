from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/oauth/authorize$', views.authorize),
    url(r'^login/oauth/access_token$', views.access_token),
    url(r'^user$', views.user),
    url(r'^logout$', views.logout),
]

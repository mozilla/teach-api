from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^access$', views.has_access),
    url(r'^login$', views.ensure_login),
    url(r'^badgelist$', views.badgelist),
    url(r'^badge/([0-9]+)$', views.badge),
    url(r'^claim/([0-9]+)$', views.claim_badge)
]

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404

from django.utils import timezone
from datetime import datetime

class UserCredlyProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=400)
    refresh_token = models.CharField(max_length=400)
    token_created = models.DateTimeField(auto_now_add=True)
    token_refreshed = models.DateTimeField(auto_now_add=True, default=timezone.now)

'''
  Create a new model record associated with an id.wmo login id
'''
def create_new_user(user_id):
    user_credly_profile, created = UserCredlyProfile.objects.get_or_create(user_id=user_id)
    if created:
        user_credly_profile.access_token = None;
        user_credly_profile.refresh_token = None;
        try:
            user_credly_profile.save()
        except Exception as error:
            print "Error while creating user model instance"

'''
  Save or update a user record if there is new token data.
'''
def save_user_token(user_id, data):
    user_credly_profile, created = UserCredlyProfile.objects.get_or_create(user_id=user_id)
    if not user_credly_profile.access_token == data["token"]:
        user_credly_profile.access_token = data["token"]
        user_credly_profile.refresh_token = data["refresh_token"]
        user_credly_profile.token_refreshed = timezone.now()
    try:
        user_credly_profile.save()
    except Exception as error:
        print "Error while saving credly token"

'''
  Retrieve an id.wmo user's stored credly access_token
'''
def get_credly_access_token(user_id):
    try:
        user_credly_profile = get_object_or_404(UserCredlyProfile, user_id=user_id)
        return user_credly_profile.access_token
    except Exception as error:
        return None

'''
  Get the age of a user's credly access_token in days
'''
def get_credly_token_age(user_id):
    try:
        user_credly_profile = get_object_or_404(UserCredlyProfile, user_id=user_id)
        if user_credly_profile.token_refreshed == None:
            return None
        delta = timezone.now() - user_credly_profile.token_refreshed
        return delta.days
    except Exception as error:
        return None

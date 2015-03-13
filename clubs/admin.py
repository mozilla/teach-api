from django.contrib import admin
from django.forms import ModelForm

from . import models
import teach.admin as teach_admin

class ClubAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if obj.location and not (obj.latitude and obj.longitude):
            try:
                obj.geocode()
            except Exception:
                pass
        obj.save()

teach_admin.site.register(models.Club, ClubAdmin)

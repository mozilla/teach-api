from django.contrib import admin
from django.forms import ModelForm

from . import models
import teach.admin as teach_admin

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created', 'modified', 'owner',
                    'is_active')

teach_admin.site.register(models.Club, ClubAdmin)

from django.contrib import admin
from django.forms import ModelForm

from . import models
import teach.admin as teach_admin

def owner_email(obj):
    return obj.owner.email

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created', 'modified', 'owner',
                    owner_email, 'status', 'is_active')
    readonly_fields = (owner_email,)

teach_admin.site.register(models.Club, ClubAdmin)

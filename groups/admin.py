from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin

class LimitedUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff')
    editor_fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return self.editor_fieldsets
        return super(LimitedUserAdmin, self).get_fieldsets(request, obj)

admin.site.unregister(User)
admin.site.register(User, LimitedUserAdmin)

from django.contrib import admin
from django.forms import ModelForm

from . import models
import teach.admin as teach_admin

# http://djangotricks.blogspot.com/2013/12/how-to-export-data-as-excel.html
def export_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse
    from django.conf import settings
    from django.utils.encoding import smart_str
    from django.core.urlresolvers import reverse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=clubs.csv'
    writer = csv.writer(response, csv.excel)
    # BOM (optional...Excel needs it to open UTF-8 file properly)
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Location"),
        smart_str(u"Email"),
        smart_str(u"Description"),
        smart_str(u"Admin URL")
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.name),
            smart_str(obj.location),
            smart_str(obj.owner.email),
            smart_str(obj.description),
            '%s%s' % (settings.ORIGIN,
                      reverse('admin:clubs_club_change', args=[obj.pk]))
        ])
    return response

export_csv.short_description = u"Export CSV"

def owner_email(obj):
    return obj.owner.email

class ClubAdmin(admin.ModelAdmin):
    actions = [export_csv]
    list_display = ('name', 'location', 'created', 'modified', 'owner',
                    owner_email, 'status', 'is_active')
    list_filter = ('status', 'is_active',)
    readonly_fields = (owner_email,)

teach_admin.site.register(models.Club, ClubAdmin)

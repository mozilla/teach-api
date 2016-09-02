from django.contrib import admin

from clubs_guides.models import ClubsGuide, Category
from clubs_guides.forms import ClubsGuideForm


@admin.register(ClubsGuide)
class ClubsGuideAdmin(admin.ModelAdmin):
    form = ClubsGuideForm

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = ClubsGuideForm
        form = super(ClubsGuideAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["translation_of"].widget.can_add_related = False
        return form

    class Meta:
        verbose_name = "clubs guide"

    class Media:
        js = ("/static/admin/js/toggle_clubs_guides_translation.js",)

admin.site.register(Category)

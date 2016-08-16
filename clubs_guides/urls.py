from django.conf.urls import url

from clubs_guides.views import (
    ClubsGuidesListView,
    ClubsGuideView,
    CategoryListView,
)


# Root URL: `/api/clubsguides` (this can be changed in the teach/urls.py file)
# NOTE: The patterns below are tacked onto the root url mentioned above

urlpatterns = [
    # `/` - Gets a list of clubs guides
    url("^$", ClubsGuidesListView.as_view(), name="clubsguide-list"),

    # `/:pk` - Gets a single clubs guide by its primary key, where the named
    # group is called pk by default in Django, (see
    # https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-display/#performing-extra-work)
    # but represents the clubs guide's `id`
    url(r"^(?P<pk>[0-9]+)", ClubsGuideView.as_view(), name="clubsguide"),

    # `/categories` - Gets a list of clubs guide categories which may also
    #       contain all the clubs guides associated with them depending on the
    #       query string value passed in.
    url(
        "^categories",
        CategoryListView.as_view(),
        name="clubsguide-category-list"
    ),
]

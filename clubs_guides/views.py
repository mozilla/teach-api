from rest_framework.generics import ListAPIView, RetrieveAPIView

from clubs_guides.models import ClubsGuide, Category
from clubs_guides.serializers import (
    ClubsGuideSerializer,
    CategorySerializer,
    CategoryWithClubsGuideSerializer,
)


class ClubsGuidesListView(ListAPIView):
    """
    A view that permits a GET to allow listing all the clubs guides
    in the database
    """
    queryset = ClubsGuide.objects.all()
    serializer_class = ClubsGuideSerializer


class ClubsGuideView(RetrieveAPIView):
    """
    A view that permits a GET to allow listing of a single clubs guide
    by providing its id.
    """
    queryset = ClubsGuide.objects.all()
    serializer_class = ClubsGuideSerializer


class CategoryListView(ListAPIView):
    """
    A view that permits a GET to allow listing all the clubs guides
    in the database

    **Query Parameters** -

    - `?expand=` - Expand related entities instead of
                   passing in just their foreign keys

        The only currently supported value is `?expand=clubsguides`
    """
    def get_queryset(self):
        if self.is_expand_clubs_guides():
            return Category.objects.collate_clubs_guides()

        return Category.objects.all()

    def get_serializer_class(self):
        if self.is_expand_clubs_guides():
            return CategoryWithClubsGuideSerializer
        else:
            return CategorySerializer

    # Check if the request asks to embed full representations of the clubs
    # guides that belong to each category
    def is_expand_clubs_guides(self):
        if hasattr(self, "expand_clubs_guides"):
            return self.expand_clubs_guides

        expand = self.request.query_params.get("expand")
        if expand is not None:
            expand = expand.split(',')
        else:
            expand = []

        self.expand_clubs_guides = "clubsguides" in expand

        return self.expand_clubs_guides

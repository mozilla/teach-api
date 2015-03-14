from rest_framework import serializers, viewsets, permissions

from .models import Club

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user

class ClubSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Club
        fields = ('url', 'name', 'website', 'description', 'location',
                  'latitude', 'longitude')

class ClubViewSet(viewsets.ModelViewSet):
    """
    Clubs can be read by anyone, but creating a new club requires
    authentication. The user who created a club is its **owner** and
    they are the only one who can make future edits to it, aside
    from staff.
    """

    queryset = Club.objects.filter(is_active=True)
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, serializer):
        instance = Club.objects.get(pk=serializer.pk)
        instance.is_active = False
        instance.save()

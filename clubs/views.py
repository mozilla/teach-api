from rest_framework import serializers, viewsets

from .models import Club

class ClubSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Club
        fields = ('name', 'website', 'description', 'location',
                  'latitude', 'longitude')

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.filter(is_active=True)
    serializer_class = ClubSerializer

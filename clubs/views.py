from django.db.models import Q
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers, viewsets, permissions

from .models import Club
from . import email

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
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ('url', 'name', 'website', 'description', 'location',
                  'latitude', 'longitude', 'owner', 'status')
        read_only_fields = ('status',)

    def get_owner(self, obj):
        return obj.owner.username

class ClubViewSet(viewsets.ModelViewSet):
    """
    Clubs can be read by anyone, but creating a new club requires
    authentication. The user who created a club is its **owner** and
    they are the only one who can make future edits to it, aside
    from staff.

    Clubs also have an approval flow they must proceed through. The
    state of this approval is reflected in the club's **status**.

    When a club is first created through the REST API, its status is
    set to `"pending"` and Teach staff are alerted through email.

    Depending on the result of review, the state may later be modified
    by Teach staff to `"approved"` or `"denied"`.

    If a club's status is pending or denied, only the club's owner
    can view it.

    If a club's status is denied and its owner updates any of the
    club's metadata, the status is changed to pending.
    """

    queryset = Club.objects.filter(is_active=True)
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get_queryset(self):
        q = Q(status=Club.APPROVED)
        if self.request.user.is_authenticated():
            q = q | Q(owner=self.request.user)
        return self.queryset.filter(q)

    def perform_create(self, serializer):
        club = serializer.save(
            owner=self.request.user,
            status=Club.PENDING
        )
        send_mail(
            subject=email.CREATE_MAIL_SUBJECT,
            message=email.CREATE_MAIL_BODY % {
                'username': self.request.user.username,
                'TEACH_SITE_URL': settings.TEACH_SITE_URL
            },
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email],
            # We don't want send failure to prevent a success response.
            fail_silently=True
        )
        if settings.TEACH_STAFF_EMAILS:
            send_mail(
                subject=email.CREATE_MAIL_STAFF_SUBJECT,
                message=email.CREATE_MAIL_STAFF_BODY % {
                    'username': self.request.user.username,
                    'email': self.request.user.email,
                    'club_name': club.name,
                    'club_location': club.location,
                    'club_website': club.website,
                    'club_description': club.description,
                    'admin_url': '%s%s' % (
                        settings.ORIGIN,
                        reverse('admin:clubs_club_change', args=(club.id,))
                    )
                },
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.TEACH_STAFF_EMAILS,
                # We don't want send failure to prevent a success response.
                fail_silently=True
            )

    def perform_update(self, serializer):
        if serializer.instance.status == Club.DENIED:
            serializer.save(status=Club.PENDING)
        else:
            serializer.save()

    def perform_destroy(self, serializer):
        instance = Club.objects.get(pk=serializer.pk)
        instance.is_active = False
        instance.save()

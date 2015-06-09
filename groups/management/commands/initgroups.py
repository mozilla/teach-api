from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

def get_perms_from_model_attr(attr):
    '''
    Any model in the Django project can define an attribute,
    such as 'teach_staff_permissions', to be a tuple
    consisting of any subset of 'add', 'change', or 'delete'.

    This function just finds all models in the Django project,
    sees if they have the given attribute, and returns the
    permission codenames for all the models.

    This ultimately allows group permissions to be defined in
    a decentralized way.
    '''

    perms = []
    for config in apps.get_app_configs():
        for model in config.get_models():
            if hasattr(model, attr):
                modelname = model.__name__.lower()
                perms.extend([
                    '%s_%s' % (perm, modelname)
                    for perm in getattr(model, attr)
                ])
    return tuple(perms)

TEACH_STAFF_PERMS = (
    'change_user',
) + get_perms_from_model_attr('teach_staff_permissions')

RC_PERMS = get_perms_from_model_attr('regional_coordinator_permissions')

class Command(BaseCommand):
    help = '''\
    Initializes some helpful initial permission groups.
    '''

    def set_perms(self, groupname, codenames):
        self.stdout.write("Setting permissions for group '%s'." % groupname)
        if self.verbosity >= 2:
            self.stdout.write("  Permissions: %s" % ', '.join(codenames))
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            group = Group(name=groupname)
            group.save()
        group.permissions = [
            Permission.objects.get(codename=codename)
            for codename in codenames
        ]
        group.save()

    def handle(self, *args, **kwargs):
        self.verbosity = int(kwargs['verbosity'])
        self.set_perms('Teach Staff', TEACH_STAFF_PERMS)
        self.set_perms('Regional Coordinators', RC_PERMS)
        self.stdout.write("Done.")
        self.stdout.write("Please do not manually change these "
                          "groups; they may be updated in the future.")

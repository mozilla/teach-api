from django_browserid.admin import BrowserIDAdminSite

class TeachAdminSite(BrowserIDAdminSite):
    site_header = 'Mozilla Learning Administration'

site = TeachAdminSite()

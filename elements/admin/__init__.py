from django.contrib import admin
from params import SiteParamsAdmin
from elements.models import SiteParams
from elements.admin import widgets

admin.site.register(SiteParams, SiteParamsAdmin)
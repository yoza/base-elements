from django.contrib import admin
from .params import SiteParamsAdmin
from elements.models import SiteParams


admin.site.register(SiteParams, SiteParamsAdmin)

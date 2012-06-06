from os.path import join
from django.contrib import admin
from django.conf import settings
import multilingual


class SiteParamsAdmin(multilingual.ModelAdmin):
    """
    Site params admin
    """
    save_on_top = True
    actions = None
    use_prepopulated_fields = {'slug': ('title', )}
    if not settings.DEBUG:
        exclude = ('ga_code',)

    use_fieldset = (
        (None, {'fields': ('site', 'rb_section', 'lb_section', 'ga_code', 'slug')}),
    )

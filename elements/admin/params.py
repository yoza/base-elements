"""
site params admin
"""
from django.conf import settings

from hvad.admin import TranslatableAdmin

from elements import settings as local_settings
from elements.admin.widgets import TinyMCE


class SiteParamsAdmin(TranslatableAdmin):
    """
    Site params admin
    """

    save_on_top = True
    actions = None

    if not settings.DEBUG:
        exclude = ('ga_code',)

    if getattr(local_settings, 'USE_TINY_MCE', False):
        def formfield_for_dbfield(self, db_field, **kwargs):
            if db_field.name == 'description':
                kwargs['widget'] = TinyMCE
                if 'request' in kwargs:
                    del kwargs['request']
                return db_field.formfield(**kwargs)
            return super(SiteParamsAdmin, self).formfield_for_dbfield(db_field,
                                                                      **kwargs)

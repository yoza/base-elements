from os.path import join
from django.contrib import admin
from django.conf import settings

class SiteParamsAdmin(admin.ModelAdmin):
    """
    Site params admin
    """
    save_on_top = True
    actions = None
    prepopulated_fields = {'slug': ('title', )}
    if not settings.DEBUG:
        exclude = ('ga_code',)

    class Media:
        css = {
            'all': [join(settings.STATIC_URL, path) for path in (
                #'pages/css/rte.css',
                #'pages/css/pages.css',
                #"pages/css/admin_fixform.css",
            )]
        }
        js = [join(settings.STATIC_URL, path) for path in (
            #'pages/js/adapter.js',
            #'pages/js/pages.js',
            #'pages/js/pages_list.js',
            #'pages/js/inline.js',
        )]



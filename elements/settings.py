# -*- coding: UTF-8 -*-
from os.path import join

from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text

# tiny_mce #
USE_TINY_MCE = getattr(settings, 'USE_TINY_MCE', False)
DEFAULT_URL_TINYMCE = getattr(settings, 'DEFAULT_URL_TINYMCE', 'tinymce/tinymce.js')
# end tiny_mce #

# hierathy manager #
HIERARHY_STATIC_URL = getattr(settings,
                              'HIERARHY_STATIC_URL',
                              join(settings.STATIC_URL, 'elements/'))
# end hierathy manager #

# range paginator #
PAGINATOR_PER_PAGE = getattr(settings, 'PAGINATOR_PER_PAGE', 10)
PAGES_PER_PAGER = getattr(settings, 'PAGES_PER_PAGER', 4)
# range paginator #

# base header #
ALTERNATE_STYLES = getattr(settings, 'ALTERNATE_STYLES', ())

settings.SEARCH_LABEL = getattr(settings, 'SEARCH_LABEL',
                                smart_text(_("Search...")))

TEMPLATE_PAGINATOR_PATH = getattr(settings, 'TEMPLATE_PAGINATOR', 'block')

#
FILEBROWSER_ADMIN = getattr(settings, 'FILEBROWSER_ADMIN', False)

# languages #
gettext_noop = lambda s: s
LANGUAGES = getattr(settings, 'LANGUAGES', (
    ('en', gettext_noop('English')),
))
HVAD_FALLBACK_LANGUAGES = getattr(settings, 'HVAD_FALLBACK_LANGUAGES', 'en')

COUNT_LANG = getattr(settings, 'COUNT_LANG', len(LANGUAGES))

# """
# LOGO
# """
APP_LABEL = getattr(settings, 'APP_LABEL', 'elements')
LOGO_IMAGE = getattr(settings, 'LOGO_IMAGE',
                     ("/static/%s/img/logo.png" % APP_LABEL, "0,0,133,133"))
GRAVATAR_EMAIL = getattr(settings, 'GRAVATAR_EMAIL', '')

# """
# Admin
# """
CSS_PATH = 'css'

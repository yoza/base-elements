# -*- coding: UTF-8 -*-
from os.path import join

from django.conf import settings


# tiny_mce #
USE_TINY_MCE = getattr(settings, 'USE_TINY_MCE', False)
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
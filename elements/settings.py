# -*- coding: UTF-8 -*-
from os.path import join

from django.conf import settings

USE_TINY_MCE = getattr(settings, 'USE_TINY_MCE', False)


HIERARHY_STATIC_URL = getattr(settings, 'HIERARHY_STATIC_URL', join(settings.STATIC_URL, 'elements/'))


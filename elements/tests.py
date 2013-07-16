"""
elements unit tests

"""
from django.conf import settings
from django.test import TestCase

from elements.models import SiteParams


class SiteParamsTestCase(TestCase):
    """
    simple unit test params
    """
    def setUp(self):
        """
        sutup
        """
        SiteParams.objects.create(site_id=settings.SITE_ID, slug="slugtest")

    def test_params_read(self):
        """
        check params read
        """
        params = SiteParams.objects.get(site_id=settings.SITE_ID)
        print params.last_update

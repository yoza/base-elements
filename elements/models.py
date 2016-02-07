"""
elements models
"""

from django.utils import timezone

from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


class SiteParams(models.Model):

    '''
    SiteParams model
    '''

    site = models.ForeignKey(Site, verbose_name=_('Site'))

    ga_code = models.TextField(_('JS code'), null=True, blank=True,
                               help_text=_('Custom JavaScript: Copy '
                                           'and paste it on this field.'))
    ga_account = models.CharField(_('GA Tracking ID'), null=True, blank=True,
                                  max_length=32,
                                  help_text=_('Google Analitics Tracking ID'))

    last_update = models.DateTimeField(_('last update time'),
                                       editable=False,
                                       db_column='last_update_time',
                                       default=timezone.now)

    title = models.CharField(_('Site title'), null=True, blank=True,
                             max_length=512,
                             help_text=_('Put here alternative text for '
                                         'logo image and site name'))
    footer = models.CharField(_('copyright'), null=True, blank=True,
                              max_length=512,
                              help_text=_('Site copyright'))
    slogan = models.CharField(_('Site slogan'), null=True,
                              blank=True, max_length=512,
                              help_text=_('Put here text for site slogan'))
    description = models.TextField(_('description'), null=True, blank=True,
                                   help_text=_('Site Description'))
    mdescrip = models.TextField(_('Meta description'), null=True, blank=True,
                                help_text=_('The site meta description'))
    mkeyword = models.TextField(verbose_name=_('Meta keywords'),
                                null=True, blank=True,
                                help_text=_("Site meta keywords. Please "
                                            "write a comma separated."))

    class Meta:
        app_label = 'elements'
        verbose_name = _('site parameter')
        verbose_name_plural = _('site parameters')
        db_table = 'elements_siteparam'

    @classmethod
    def invalidate(cls):
        """
        invalidate
        """
        pass

    def __str__(self):
        """
        unicode
        """
        prefix = _('Parameters data for site')
        if self.title:
            prefix = '{} - '.format(self.title)

        return '{} ({})'.format(prefix, self.site.domain)

    def save(self, *args, **kwargs):
        """
        save
        """
        self.last_update = timezone.now()
        super(SiteParams, self).save(*args, **kwargs)
    save.alters_data = True

"""
elements models
"""
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from hvad.models import TranslatableModel, TranslatedFields
from hvad.manager import TranslationManager


class SiteParamsManager(TranslationManager):

    """
    manager
    """
    pass


@python_2_unicode_compatible
class SiteParams(TranslatableModel):

    '''
    SiteParams model

    '''
    if settings.USE_TZ:
        date_time_now = timezone.now()
    else:
        date_time_now = datetime.utcnow()

    site = models.ForeignKey(Site, verbose_name=_('Site'))
    rb_section = models.BooleanField(verbose_name=_('Right sidebar'),
                                     default=False,
                                     help_text=_('Show/hide right sidebar on '
                                                 'the main page'))
    lb_section = models.BooleanField(verbose_name=_('Left sidebar'),
                                     default=False,
                                     help_text=_('Show/hide left sidebar on '
                                                 'the main page'))
    ga_code = models.TextField(_('JS code'), null=True, blank=True,
                               help_text=_('Custom JavaScript: Copy '
                                           'and paste it on this field.'))
    ga_account = models.CharField(_('GA Tracking ID'), null=True, blank=True,
                                  max_length=32,
                                  help_text=_('Google Analitics Tracking ID'))
    slug = models.SlugField(_(u'slug'), null=False, blank=False,
                            max_length=128, unique=True,
                            help_text=_('site params slug'))
    last_update = models.DateTimeField(_('last update time'),
                                       editable=False,
                                       db_column='last_update_time',
                                       default=date_time_now)

    objects = SiteParamsManager()

    class Meta:
        verbose_name = _('site parameter')
        verbose_name_plural = _('site parameters')
        db_table = u'element_siteparam'

    translations = TranslatedFields(
        title=models.CharField(_('Site title'), null=True,
                               blank=True, max_length=512,
                               help_text=_('Put here alternative text for '
                                           'logo image and site name')),
        footer=models.CharField(_('copyright'), null=True, blank=True,
                                max_length=512,
                                help_text=_('Site copyright')),
        slogan=models.CharField(_('Site slogan'), null=True,
                                blank=True, max_length=512,
                                help_text=_('Put here text for site slogan')),
        description=models.TextField(_('description'), null=True, blank=True,
                                     help_text=_('Site Description')),
        mdescrip=models.TextField(_('Meta description'), null=True, blank=True,
                                  help_text=_('The site meta description')),
        mkeyword=models.TextField(verbose_name=_('Meta keywords'),
                                  null=True, blank=True,
                                  help_text=_("Site meta keywords. Please "
                                              "write a comma separated."))
    )

    def invalidate(self):
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
            prefix += ' - ' + self.title

        return prefix + ' (' + self.site.domain + ')'

    def save(self, *args, **kwargs):
        """
        save
        """
        self.last_update = self.date_time_now
        super(SiteParams, self).save(*args, **kwargs)
    save.alters_data = True

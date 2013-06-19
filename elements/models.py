"""
elements models
"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site

from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields
from hvad.manager import TranslationManager


class SiteParamsManager(TranslationManager):
    pass


class SiteParams(TranslatableModel):
    '''
    SiteParams model

    '''
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    rb_section = models.BooleanField(verbose_name=_('Right block'),
                                     default=False,
                                     help_text=_('Show/hide right block on '
                                                 'the main page'))
    lb_section = models.BooleanField(verbose_name=_('Left block'),
                                     default=False,
                                     help_text=_('Show/hide left block on '
                                                 'the main page'))
    ga_code = models.TextField(_('GA code'), null=True, blank=True,
                               help_text=_('Custom JavaScript: Google '
                                           'Analitics JS code etc. Copy and '
                                           'paste it on this field.'))
    slug = models.SlugField(_(u'slug'), null=False, blank=False,
                            max_length=128, unique=True,
                            help_text=_('site params slug'))
    last_update = models.DateTimeField(_('last update time'),
                                       editable=False,
                                       db_column='last_update_time',
                                       default=datetime.utcnow())
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

    def __unicode__(self):
        """
        unicode
        """
        prefix = _('Parameters data for site')
        return prefix + ' - ' + self.title + ' (' + self.site.domain + ')'

    def save(self, *args, **kwargs):
        """
        save
        """
        self.last_update = datetime.utcnow()
        super(SiteParams, self).save(*args, **kwargs)
    save.alters_data = True

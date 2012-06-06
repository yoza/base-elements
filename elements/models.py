from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields
from hvad.manager import TranslationManager


class SiteParamsMamager(TranslationManager):
    pass


class SiteParams(TranslatableModel):
    '''
    SiteParams model

    '''
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    rb_section = models.BooleanField(verbose_name=_('Right block'),
                                     default=True,
                                     help_text=_('''Show/hide right block on main page'''))
    lb_section = models.BooleanField(verbose_name=_('Left block'),
                                     default=False,
                                     help_text=_('''Show/hide left block on main page'''))
    ga_code = models.TextField(_('GA code'), null=True, blank=True,
                               help_text=_('''Custom JavaScript: Google Analitics JS code etc. Copy and paste it on this field.'''))
    slug = models.SlugField(_(u'slug'), null=False, blank=False,
                            max_length=128, unique=True,
                            help_text=_('site params slug'))

    objects = SiteParamsMamager()

    class Meta:
        verbose_name = _('site parameter')
        verbose_name_plural = _('site parameters')

    translations = TranslatedFields(
        title = models.CharField(_('Site title'), null=True,
                                 blank=True, max_length=512,
                                 help_text=_('''Put here alternative text for logo image and site name''')),
        footer = models.CharField(_('copyright'), null=True,
                                  blank=True, max_length=512,
                                  help_text=_('''Site copyright''')),
        slogan = models.CharField(_('Site slogan'), null=True,
                                  blank=True, max_length=512,
                                  help_text=_('''Put here text for site slogan''')),
    )

    def invalidate(self):
        pass

    def __unicode__(self):
        prefix = _('Parameters data for site')
        return prefix + ' - ' + self.title + ' (' + self.site.domain + ')'

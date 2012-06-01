from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


class SiteParams(models.Model):
    '''
    SiteParams model

    '''
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    footer = models.CharField(_('copyright'), null=True,
                              blank=True, max_length=512,
                              help_text=_('''Site copyright'''))
    title = models.CharField(_('Site title'), null=True,
                             blank=True, max_length=512,
                             help_text=_('''Put here alternative text \
                                         for logo image and site name'''))
    slug = models.SlugField(_(u'slug'), null=False, blank=False,
                            max_length=128, unique=True,
                            help_text=_('site params slug'))
    slogan = models.CharField(_('Site slogan'), null=True,
                              blank=True, max_length=512,
                              help_text=_('''Put here text for site slogan'''))

    rb_section = models.BooleanField(verbose_name=_('Right block'),
                                     default=True,
                                     help_text=_('''Show/hide right block on \
                                                 main page'''))
    lb_section = models.BooleanField(verbose_name=_('Left block'),
                                     default=False,
                                     help_text=_('''Show/hide left block on \
                                                 main page'''))
    ga_code = models.TextField(_('GA code'), null=True, blank=True,
                               help_text=_('''Google Analitics JS code. Copy \
                                           and paste it on this field.'''))

    class Meta:
        verbose_name = _('site parameter')
        verbose_name_plural = _('site parameters')

    def invalidate(self):
        pass

    def __unicode__(self):
        prefix = _('Parameters data for site')
        return prefix + ' - ' + self.title + ' (' + self.site.domain + ')'

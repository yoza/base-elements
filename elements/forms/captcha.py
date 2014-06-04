from django.utils import six
from django.forms.forms import DeclarativeFieldsMetaclass
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms import Widget, Field, BaseForm, Form, ValidationError
from django.utils import translation
from django.utils.safestring import mark_safe

from recaptcha.client import captcha


class RecaptchaWidget(Widget):
    def __init__(self, theme=None, tabindex=None, use_ssl=None):
        options = {}
        if theme:
            options['theme'] = theme
        if tabindex:
            options['tabindex'] = tabindex
        self.options = options
        self.use_ssl = \
            use_ssl if use_ssl is not None else getattr(settings,
                                                        'RECAPTCHA_USE_SSL',
                                                        False)
        super(RecaptchaWidget, self).__init__()

    def render(self, name, value, attrs=None):
        self.options['lang'] = lang = translation.get_language()
        if len(settings.RECAPTCHA_CUSTOM_TRANSLATIONS[lang]) > 0:
            self.options['custom_translations'] = \
                settings.RECAPTCHA_CUSTOM_TRANSLATIONS[lang]
            options = '%r' % self.options
            options = options.replace("u'", "'")
        else:
            options = '%r' % self.options
        res = """<script type="text/javascript">
                    var RecaptchaOptions = %s;
                 </script>""" % options

        return mark_safe(
            res + captcha.displayhtml(settings.RECAPTCHA_PUB_KEY,
                                      self.use_ssl))

    def value_from_datadict(self, data, files, name):
        challenge = data.get('recaptcha_challenge_field')
        response = data.get('recaptcha_response_field')
        return (challenge, response)

    @classmethod
    def id_for_label(cls, _id):
        return _id
    #id_for_label = classmethod(id_for_label)
        #return None


class RecaptchaField(Field):
    widget = RecaptchaWidget

    def __init__(self, remote_ip, *args, **kwargs):
        self.remote_ip = remote_ip
        super(RecaptchaField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(RecaptchaField, self).clean(value)
        challenge, response = value
        if not challenge:
            raise ValidationError(_('An error occured with the CAPTCHA '
                                    'service. Please try again.'))
        if not response:
            raise ValidationError(_('Please enter the CAPTCHA solution.'))

        check_captcha = captcha.submit(challenge,
                                       response,
                                       settings.RECAPTCHA_PRIVATE_KEY,
                                       self.remote_ip)

        if not check_captcha.is_valid:
            raise ValidationError(_('An incorrect CAPTCHA solution was '
                                    'entered.'))
        return value


class RecaptchaFieldPlaceholder(Field):
    '''
    Placeholder field for use with RecaptchaBaseForm which gets replaced with
    RecaptchaField (which is passed the remote_ip) when RecaptchaBaseForm is
    initialised.
    '''
    def __init__(self, *args, **kwargs):
        super(RecaptchaFieldPlaceholder, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs


class RecaptchaBaseForm(six.with_metaclass(DeclarativeFieldsMetaclass,
                                           BaseForm)):

    __metaclass__ = DeclarativeFieldsMetaclass

    def __init__(self, request, *args, **kwargs):
        for key, field in self.base_fields.items():
            if isinstance(field, RecaptchaFieldPlaceholder):
                self.base_fields[key] = \
                    RecaptchaField(request.META.get('REMOTE_ADDR', ''),
                                   *field.args, **field.kwargs)
        super(RecaptchaBaseForm, self).__init__(*args, **kwargs)


class RecaptchaForm(six.with_metaclass(DeclarativeFieldsMetaclass,
                                       RecaptchaBaseForm, Form)):
    """
    RECAPTCHA form
    """
    __metaclass__ = DeclarativeFieldsMetaclass

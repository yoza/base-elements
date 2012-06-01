from django.conf import settings
from recaptcha.client import captcha
from django.utils.translation import ugettext_lazy as _
from django.forms import Widget, Field, BaseForm, Form, ValidationError
from django.utils import translation
from django.utils.safestring import mark_safe


class RecaptchaWidget(Widget):
    def __init__(self, theme=None, tabindex=None):
        options = {}
        if theme:
            options['theme'] = theme
        if tabindex:
            options['tabindex'] = tabindex
        self.options = options
        super(RecaptchaWidget, self).__init__()

    def render(self, name, value, attrs=None):
        self.options['lang'] = translation.get_language()
        if len(settings.RECAPTCHA_CUSTOM_TRANSLATIONS[self.options['lang']]) >\
                                                                             0:
            self.options['custom_translations'] = \
                   settings.RECAPTCHA_CUSTOM_TRANSLATIONS[self.options['lang']]
            options = '%r' % self.options
            options = options.replace("u'", "'")
        else:
            options = '%r' % self.options
        res = """<script type="text/javascript">
                    var RecaptchaOptions = %s;
                 </script>""" % options

        result = mark_safe(res + \
                           captcha.displayhtml(settings.RECAPTCHA_PUB_KEY))
        return result

    def value_from_datadict(self, data, files, name):
        challenge = data.get('recaptcha_challenge_field')
        response = data.get('recaptcha_response_field')
        return (challenge, response)

    def id_for_label(self, id_):
        return id_
    id_for_label = classmethod(id_for_label)
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
            e = _('An error occured with the CAPTCHA service.\
                  Please try again.')
            raise ValidationError(e)
        if not response:
            raise ValidationError(_('Please enter the CAPTCHA solution.'))

        check_captcha = captcha.submit(challenge,
                                       response,
                                       settings.RECAPTCHA_PRIVATE_KEY,
                                       self.remote_ip)

        if not check_captcha.is_valid:
            e = _('An incorrect CAPTCHA solution was entered.')
            raise ValidationError(e)
        return value


class RecaptchaFieldPlaceholder(Field):
    '''
    Placeholder field for use with RecaptchaBaseForm which gets replaced with
    RecaptchaField (which is passed the remote_ip) when RecaptchaBaseForm is
    initialised.
    '''
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class RecaptchaBaseForm(BaseForm):
    def __init__(self, request, *args, **kwargs):
        for key, field in self.base_fields.items():
            if isinstance(field, RecaptchaFieldPlaceholder):
                self.base_fields[key] = \
                        RecaptchaField(request.META.get('REMOTE_ADDR', ''),
                                       *field.args, **field.kwargs)
        super(RecaptchaBaseForm, self).__init__(*args, **kwargs)


class RecaptchaForm(RecaptchaBaseForm, Form):
    pass

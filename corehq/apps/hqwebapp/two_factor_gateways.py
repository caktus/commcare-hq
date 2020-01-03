from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils import translation
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from requests.compat import getproxies
from six.moves.urllib.parse import urlencode
from tastypie.http import HttpTooManyRequests
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client

import settings
from corehq.messaging.smsbackends.twilio.models import SQLTwilioBackend
from corehq.project_limits.rate_limiter import RateLimiter, get_dynamic_rate_definition, \
    RateDefinition
from corehq.util.datadog.gauges import datadog_counter, datadog_gauge
from corehq.util.decorators import run_only_when, silence_and_report_error
from corehq.util.global_request import get_request
from dimagi.utils.web import get_ip

VOICE_LANGUAGES = ('en', 'en-gb', 'es', 'fr', 'it', 'de', 'da-DK', 'de-DE',
                   'en-AU', 'en-CA', 'en-GB', 'en-IN', 'en-US', 'ca-ES',
                   'es-ES', 'es-MX', 'fi-FI', 'fr-CA', 'fr-FR', 'it-IT',
                   'ja-JP', 'ko-KR', 'nb-NO', 'nl-NL', 'pl-PL', 'pt-BR',
                   'pt-PT', 'ru-RU', 'sv-SE', 'zh-CN', 'zh-HK', 'zh-TW')


class Gateway(object):

    def __init__(self):
        backends = SQLTwilioBackend.objects.filter(hq_api_id='TWILIO', deleted=False, is_global=True)
        sid = backends[0].extra_fields['account_sid']
        token = backends[0].extra_fields['auth_token']
        self.from_number = backends[0].load_balancing_numbers[0]
        self.client = self._get_client(sid, token)

    def _get_client(self, sid, token):
        proxy_client = TwilioHttpClient()
        proxy_client.session.proxies = getproxies()
        return Client(sid, token, http_client=proxy_client)

    def send_sms(self, device, token):
        if rate_limit_two_factor_setup(method='sms'):
            return HttpTooManyRequests()

        message = _('Your authentication token is %s') % token
        self.client.api.account.messages.create(
            to=device.number.as_e164,
            from_=self.from_number,
            body=message)

    def make_call(self, device, token):
        if rate_limit_two_factor_setup(method='call'):
            return HttpTooManyRequests()

        locale = translation.get_language()
        validate_voice_locale(locale)

        url = reverse('two_factor:twilio_call_app', kwargs={'token': token})
        url = '%s?%s' % (url, urlencode({'locale': locale}))
        uri = 'https://%s%s' % (Site.objects.get_current().domain, url)
        self.client.api.account.calls.create(to=device.number.as_e164, from_=self.from_number,
                                 url=uri, method='GET', if_machine='Hangup', timeout=15)


def validate_voice_locale(locale):
    with translation.override(locale):
        voice_locale = pgettext('twilio_locale', 'en')
        if voice_locale not in VOICE_LANGUAGES:
            raise NotImplementedError('The language "%s" is not '
                                      'supported by Twilio' % voice_locale)


@run_only_when(not settings.ENTERPRISE_MODE and not settings.UNIT_TESTING)
@silence_and_report_error("Exception raised in the two factor setup rate limiter",
                          'commcare.two_factor.setup_rate_limiter_errors')
def rate_limit_two_factor_setup(method):
    """
    This holds attempts per user AND attempts per IP below limits

    given by two_factor_setup_rate_limiter.
    And keeps total requests below limits given by global_two_factor_setup_rate_limiter.

    Requests without a username or IP are rejected (unusual).

    """
    _status_rate_limited = 'rate_limited'
    _status_bad_request = 'bad_request'
    _status_accepted = 'accepted'
    _status_missing_username = 'missing_username:ip:{}'

    def get_ip_and_username():
        request = get_request()
        if request:
            ip_address = get_ip(request)
            username = request.user.username if getattr(request, 'user', None) else None
            return ip_address, username
        else:
            return None, None

    _report_current_global_two_factor_setup_rate_limiter()

    ip_address, username = get_ip_and_username()

    if ip_address and username:
        if two_factor_setup_rate_limiter.allow_usage('ip:{}'.format(ip_address)) \
                and two_factor_setup_rate_limiter.allow_usage('user:{}'.format(username)) \
                and global_two_factor_setup_rate_limiter.allow_usage():
            two_factor_setup_rate_limiter.report_usage('ip:{}'.format(ip_address))
            two_factor_setup_rate_limiter.report_usage('user:{}'.format(username))
            global_two_factor_setup_rate_limiter.report_usage()
            status = _status_accepted
        else:
            status = _status_rate_limited
    elif ip_address:
        status = _status_missing_username.format(ip_address)
    else:
        status = _status_bad_request

    datadog_counter('commcare.two_factor.setup_requests', 1, tags=[
        'status:{}'.format(status),
        'method:{}'.format(method),
    ])
    return status != _status_accepted


two_factor_setup_rate_limiter = RateLimiter(
    feature_key='two_factor_setup_attempts',
    get_rate_limits=lambda scope: get_dynamic_rate_definition(
        'two_factor_setup_attempts',
        default=RateDefinition(
            per_week=15,
            per_day=8,
            per_hour=5,
            per_minute=3,
            per_second=1,
        )
    ).get_rate_limits(),
    scope_length=1,  # per user OR per IP
)

global_two_factor_setup_rate_limiter = RateLimiter(
    feature_key='global_two_factor_setup_attempts',
    get_rate_limits=lambda: get_dynamic_rate_definition(
        'global_two_factor_setup_attempts',
        default=RateDefinition(
            per_day=100,
        )
    ).get_rate_limits(),
    scope_length=0,
)


def _report_current_global_two_factor_setup_rate_limiter():
    for window, value, threshold in global_two_factor_setup_rate_limiter.iter_rates():
        datadog_gauge('commcare.two_factor.global_two_factor_setup_threshold', threshold, tags=[
            'window:{}'.format(window)
        ])
        datadog_gauge('commcare.two_factor.global_two_factor_setup_usage', value, tags=[
            'window:{}'.format(window)
        ])

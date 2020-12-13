from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now
from pytz import timezone

from .models import Currency, ExchangeRate
from .views import CurrentExchangeRatesView


class CurrentExchangeRatesViewQueryTestCase(TestCase):
    settings_time_zone = timezone(settings.TIME_ZONE)
    one_day = timedelta(hours=24)
    exchange_rate_data_records = [
        {'currency': 'PLN', 'value': Decimal('4.4358'), 'value_time': now() - one_day * 4},
        {'currency': 'PLN', 'value': Decimal('4.4458'), 'value_time': now() - one_day * 3},
        {'currency': 'PLN', 'value': Decimal('4.4558'), 'value_time': now() - one_day * 2},
        {'currency': 'PLN', 'value': Decimal('4.4658'), 'value_time': now() - one_day},
        {'currency': 'PLN', 'value': Decimal('4.4758'), 'value_time': now()},
        # note, there are less 'PHP' records then they are others
        {'currency': 'PHP', 'value': Decimal('58.339'), 'value_time': now() - one_day * 4},
        {'currency': 'PHP', 'value': Decimal('58.349'), 'value_time': now() - one_day * 3},
        {'currency': 'PHP', 'value': Decimal('58.359'), 'value_time': now() - one_day * 2},
        {'currency': 'PHP', 'value': Decimal('58.369'), 'value_time': now() - one_day},

        {'currency': 'USD', 'value': Decimal('1.2127'), 'value_time': now() - one_day * 4},
        {'currency': 'USD', 'value': Decimal('1.2027'), 'value_time': now() - one_day * 3},
        {'currency': 'USD', 'value': Decimal('1.1927'), 'value_time': now() - one_day * 2},
        {'currency': 'USD', 'value': Decimal('1.1827'), 'value_time': now() - one_day},
        {'currency': 'USD', 'value': Decimal('1.1727'), 'value_time': now()},
    ]

    @property
    def currencies(self):
        return {r['currency'] for r in self.exchange_rate_data_records}

    def setUp(self) -> None:
        currencies = {}
        for name in self.currencies:
            currencies[name] = Currency.objects.create(name=name)

        for erdr in self.exchange_rate_data_records:
            ExchangeRate.objects.create(
                currency=currencies[erdr['currency']], value=erdr['value'], value_time=erdr['value_time']
            )

    def _get_latest_for_currency(self, currency_name: str):
        """
        Returns latest entry from exchange_rate_data_records, for given currency
        """
        result = None
        for erdr in self.exchange_rate_data_records:
            if erdr['currency'] == currency_name:
                if result is None or result['value_time'] < erdr['value_time']:
                    result = erdr
        return result

    def test_query(self):
        view = CurrentExchangeRatesView()
        queryset = view.get_queryset()

        self.assertEqual(len(queryset), len(self.currencies))
        self.assertEqual({r.name for r in queryset}, self.currencies)

        for record in queryset:
            latest = self._get_latest_for_currency(record.name)
            self.assertEqual(record.value, latest['value'])
            self.assertEqual(record.value_time.astimezone(self.settings_time_zone), latest['value_time'])


from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True, verbose_name="Nazwa")


class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, related_name='rates',
                                 on_delete=models.CASCADE)
    value = models.DecimalField(decimal_places=4, max_digits=8,
                                verbose_name="Wartość względem EUR")
    value_time = models.DateTimeField(verbose_name="Stan na czas")

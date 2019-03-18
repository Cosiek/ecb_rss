#!/usr/bin/env python
# coding: utf-8

from rest_framework import serializers

from .models import Currency, ExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExchangeRate
        fields = ('value', 'value_time')


class HistoricExchangeRatesSerializer(serializers.ModelSerializer):
    rates = ExchangeRateSerializer(many=True, read_only=True)

    class Meta:
        model = Currency
        fields = ('name', 'rates')

#!/usr/bin/env python
# coding: utf-8

from decimal import Decimal

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


class CurrentExchangeRatesSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    value_time = serializers.DateTimeField()

    class Meta:
        model = Currency
        fields = ('name', 'value', 'value_time')

    def get_value(self, obj):
        return Decimal(obj.value)

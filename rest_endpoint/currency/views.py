#!/usr/bin/env python
# coding: utf-8

from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Currency
from .serializers import (CurrentExchangeRatesSerializer,
                          HistoricExchangeRatesSerializer)


class HistoricExchangeRatesView(APIView):
    serializer_class = HistoricExchangeRatesSerializer

    def get(self, request, format=None):
        name = request.GET.get('name')
        qs = Currency.objects.all().order_by('rates__value_time')
        cu = get_object_or_404(qs, name=name)
        serializer = HistoricExchangeRatesSerializer(cu)
        return Response(serializer.data)


class CurrentExchangeRatesView(APIView):

    def get(self, request, format=None):
        qs = self.get_queryset()
        serializer = CurrentExchangeRatesSerializer(qs, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        sql = (
            "SELECT currency_currency.id, currency_currency.name, "
                "currency_exchangerate.value, currency_exchangerate.value_time "
            "FROM currency_exchangerate "
            "JOIN currency_currency "
            "ON currency_currency.id = currency_exchangerate.currency_id "
            "JOIN ("
                "SELECT currency_id, MAX(value_time) AS value_time "
                "FROM currency_exchangerate "
                "GROUP BY currency_id"
            ") AS last_updated_at "
            "ON currency_exchangerate.currency_id = last_updated_at.currency_id "
            "WHERE last_updated_at.value_time = currency_exchangerate.value_time"
        )
        return Currency.objects.raw(sql)

#!/usr/bin/env python
# coding: utf-8
from django.db.models import OuterRef, Subquery, Max
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Currency, ExchangeRate
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
        # NOTE: using a raw SQL as done in commit 5c9dfdb729021caf529c656290d394ed2e436acb is significantly faster
        sq = ExchangeRate.objects.filter(currency_id=OuterRef('pk')).order_by('-value_time')
        return Currency.objects.annotate(value=Subquery(sq.values('value')[:1]), value_time=Max('rates__value_time'))

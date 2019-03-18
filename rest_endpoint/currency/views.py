#!/usr/bin/env python
# coding: utf-8

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Currency
from .serializers import HistoricExchangeRatesSerializer


class HistoricExchangeRatesView(APIView):
    serializer_class = HistoricExchangeRatesSerializer

    def get(self, request, format=None):
        name = request.GET.get('name')
        qs = Currency.objects.all().order_by('rates__value_time')
        cu = get_object_or_404(qs, name=name)
        serializer = HistoricExchangeRatesSerializer(cu)
        return Response(serializer.data)

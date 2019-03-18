#!/usr/bin/env python3.6
# encoding: utf-8

from django.contrib import admin
from django.urls import path

from rest_endpoint.currency import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('history', views.HistoricExchangeRatesView.as_view()),
]

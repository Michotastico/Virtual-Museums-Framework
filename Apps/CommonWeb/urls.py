#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"

from django.conf.urls import url
import views
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
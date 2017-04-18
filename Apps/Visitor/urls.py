#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from Apps.Visitor.views import IndexView, NoExpositionView

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^error', NoExpositionView.as_view(), name='error'),
]
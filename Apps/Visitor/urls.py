#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from Apps.Visitor.views import IndexView, NoExhibitionView, OpinionsView, VisualizationView

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^visualization', VisualizationView.as_view(), name='visualization'),
    url(r'^error', NoExhibitionView.as_view(), name='error'),
    url(r'^send-opinion', OpinionsView.as_view(), name='send-opinion'),
]
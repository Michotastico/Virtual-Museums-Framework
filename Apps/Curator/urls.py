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
    url(r'^opinions$', views.OpinionsView.as_view(), name='opinions'),
    url(r'^resources$', views.ResourcesView.as_view(), name='resources'),
    url(r'^new-resources$', views.NewResourcesView.as_view(), name='resources'),
    url(r'^rooms$', views.RoomsView.as_view(), name='rooms'),
    url(r'^new-rooms$', views.NewRoomsView.as_view(), name='new-rooms'),
    url(r'^scheduling$', views.SchedulingView.as_view(), name='scheduling'),
    url(r'^scheduling-exposition$', views.SchedulingExpositionView.as_view(), name='scheduling'),
]
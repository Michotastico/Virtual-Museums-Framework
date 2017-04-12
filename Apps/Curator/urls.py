#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Apps.Curator.views.general import IndexView, CuratorAccount
from Apps.Curator.views.museums import MuseumsView, AddUnityView
from Apps.Curator.views.opinions import OpinionsView
from Apps.Curator.views.resources import ResourcesView, NewResourcesView
from Apps.Curator.views.rooms import RoomsView, NewRoomsView
from Apps.Curator.views.scheduling import SchedulingView, SchedulingExpositionView

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"

from django.conf.urls import url

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^opinions$', OpinionsView.as_view(), name='opinions'),
    url(r'^resources$', ResourcesView.as_view(), name='resources'),
    url(r'^new-rooms$', NewRoomsView.as_view(), name='new-rooms'),
    url(r'^scheduling$', SchedulingView.as_view(), name='scheduling'),
    url(r'^scheduling-exposition$', SchedulingExpositionView.as_view(), name='scheduling'),
    url(r'^account$', CuratorAccount.as_view(), name='account'),

    url(r'^add-unity-museum$', AddUnityView.as_view(), name='new-unity'),
    url(r'^museums$', MuseumsView.as_view(), name='museums'),

    url(r'^new-resources$', NewResourcesView.as_view(), name='resources'),
    url(r'^rooms$', RoomsView.as_view(), name='rooms'),
]
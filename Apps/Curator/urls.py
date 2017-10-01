#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Apps.Curator.views.general import IndexView, CuratorAccount
from Apps.Curator.views.museums import ExhibitView, AddUnityView, PreviewExhibitView, AddVideoView, AddPDFView, \
    AddURLView, RenderHTTPonHTTPSView
from Apps.Curator.views.opinions import OpinionsView, OpinionDeleterView
from Apps.Curator.views.resources import ResourcesView, NewResourcesView
from Apps.Curator.views.scheduling import SchedulingView, SchedulingExhibitionView

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"

from django.conf.urls import url

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^opinions$', OpinionsView.as_view(), name='opinions'),
    url(r'^resources$', ResourcesView.as_view(), name='resources'),
    url(r'^scheduling$', SchedulingView.as_view(), name='scheduling'),
    url(r'^scheduling-exhibition', SchedulingExhibitionView.as_view(), name='scheduling'),
    url(r'^account$', CuratorAccount.as_view(), name='account'),

    url(r'^add-unity-exhibit', AddUnityView.as_view(), name='new-unity'),
    url(r'^add-video-exhibit', AddVideoView.as_view(), name='new-video'),
    url(r'^add-pdf-exhibit', AddPDFView.as_view(), name='new-pdf'),
    url(r'^add-url-exhibit', AddURLView.as_view(), name='new-url'),
    url(r'^iframe-safe', RenderHTTPonHTTPSView.as_view(), name='iframe-safe'),

    url(r'^exhibits', ExhibitView.as_view(), name='exhibits'),
    url(r'^exhibit-preview$', PreviewExhibitView.as_view(), name='exhibit-preview'),

    url(r'^new-resources$', NewResourcesView.as_view(), name='resources'),

    url(r'^timeout_opinions_deleter$', OpinionDeleterView.as_view(), name='deleter'),
]
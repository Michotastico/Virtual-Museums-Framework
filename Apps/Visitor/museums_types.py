#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.db import transaction

from Apps.Curator.models.museums import UnityExhibit, VideoExhibit, PDFExhibit, URLExhibit
from Apps.Curator.views.resources_types import parse_inner_url

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


@transaction.atomic
def get_unity_exhibit(exhibit):

    arguments = dict()

    arguments['title'] = exhibit.name
    arguments['id'] = exhibit.id

    exhibit = UnityExhibit.objects.get(id=exhibit.id)
    arguments['data'] = parse_inner_url(exhibit.data.url)
    arguments['js'] = parse_inner_url(exhibit.javascript.url)
    arguments['mem'] = parse_inner_url(exhibit.memory.url)
    arguments['total_memory'] = exhibit.memory_to_allocate

    return arguments


@transaction.atomic
def get_video_exhibit(exhibit):

    arguments = dict()

    arguments['title'] = exhibit.name
    arguments['id'] = exhibit.id

    exhibit = VideoExhibit.objects.get(id=exhibit.id)
    arguments['video'] = parse_inner_url(exhibit.video.url)
    extension = os.path.splitext(arguments['video'])[1].replace(".", "")
    arguments['type'] = extension

    return arguments


@transaction.atomic
def get_pdf_exhibit(exhibit):

    arguments = dict()

    arguments['title'] = exhibit.name
    arguments['id'] = exhibit.id

    exhibit = PDFExhibit.objects.get(id=exhibit.id)
    arguments['pdf'] = parse_inner_url(exhibit.pdf.url)

    return arguments


@transaction.atomic
def get_url_exhibit(exhibit):

    arguments = dict()

    arguments['title'] = exhibit.name

    exhibit = URLExhibit.objects.get(id=exhibit.id)
    arguments['uuid'] = exhibit.uuid

    return arguments


MUSEUM_TYPES = {
    'Unity': {'get': get_unity_exhibit,
              'template': 'visitor/visualizations/unity-visualization.html'},
    'Video': {'get': get_video_exhibit,
              'template': 'visitor/visualizations/video-visualization.html'},
    'Pdf': {'get': get_pdf_exhibit,
            'template': 'visitor/visualizations/pdf-visualization.html'},
    'Url': {'get': get_url_exhibit,
            'template': 'visitor/visualizations/url-visualization.html'}
}
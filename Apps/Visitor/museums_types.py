#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import transaction

from Apps.Curator.models.museums import UnityExhibit
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


MUSEUM_TYPES = {
    'Unity': {'get': get_unity_exhibit,
              'template': 'visitor/visualizations/unity-visualization.html'}
}
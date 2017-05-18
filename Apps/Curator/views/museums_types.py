#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.db import transaction

from Apps.Curator.models.museums import UnityExhibit, VideoExhibit
from Apps.Curator.views.resources_types import parse_inner_url

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


def delete_unity_files(exhibit_id):
    unity_exhibit = UnityExhibit.objects.get(id=exhibit_id)

    memory = unity_exhibit.memory.path
    javascript = unity_exhibit.javascript.path
    data = unity_exhibit.data.path

    def delete():
        os.remove(memory)
        os.remove(javascript)
        os.remove(data)

    return delete


@transaction.atomic
def get_unity_data(exhibit):
    data = dict()

    data['title'] = exhibit.name
    exhibit = UnityExhibit.objects.get(id=exhibit.id)
    data['data'] = parse_inner_url(exhibit.data.url)
    data['js'] = parse_inner_url(exhibit.javascript.url)
    data['mem'] = parse_inner_url(exhibit.memory.url)
    data['total_memory'] = exhibit.memory_to_allocate

    return data


def delete_video_files(exhibit_id):
    video_exhibit = VideoExhibit.objects.get(id=exhibit_id)

    video = video_exhibit.video.path

    def delete():
        os.remove(video)

    return delete


@transaction.atomic
def get_video_data(exhibit):
    data = dict()

    data['title'] = exhibit.name
    exhibit = VideoExhibit.objects.get(id=exhibit.id)
    data['video'] = parse_inner_url(exhibit.video.url)
    extension = os.path.splitext(data['video'])[1].replace(".", "")
    data['type'] = extension

    return data


MUSEUM_TYPES = {
    'Unity': {'delete': delete_unity_files, 'get': get_unity_data,
              'template': 'curator/preview_exhibits/preview_unity.html'},
    'Video': {'delete': delete_video_files, 'get': get_video_data,
              'template': 'curator/preview_exhibits/preview_video.html'}
}
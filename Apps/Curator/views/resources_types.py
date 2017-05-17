#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from django.db import transaction

from Apps.Curator.forms import MusicForm, ImageForm, ModelForm, VideoForm
from Apps.Curator.models.resources import ExternalMusic, ExternalVideo, ExternalImage, ExternalModel

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


def parse_inner_url(url):
    return re.sub(r'.*/static', '/static', url)


@transaction.atomic
def query_music():
    music_list = list()
    musics = ExternalMusic.objects.all()
    for music in musics:
        music_template = dict()
        music_template['id'] = music.id
        music_template['title'] = music.title
        music_template['description'] = music.description
        music_template['href'] = parse_inner_url(music.file.url)
        music_list.append(music_template)
    return music_list


@transaction.atomic
def delete_music(_id):
    music = ExternalMusic.objects.get(id=_id)
    path = music.file.path
    music.delete()
    os.remove(path)


@transaction.atomic
def query_video():
    video_list = list()
    videos = ExternalVideo.objects.all()
    for video in videos:
        video_template = dict()
        video_template['id'] = video.id
        video_template['title'] = video.title
        video_template['description'] = video.description
        video_template['href'] = parse_inner_url(video.file.url)
        video_list.append(video_template)
    return video_list


@transaction.atomic
def delete_video(_id):
    video = ExternalVideo.objects.get(id=_id)
    path = video.file.path
    video.delete()
    os.remove(path)


@transaction.atomic
def query_image():
    image_list = list()
    images = ExternalImage.objects.all()
    for image in images:
        image_template = dict()
        image_template['id'] = image.id
        image_template['title'] = image.title
        image_template['description'] = image.description
        image_template['href'] = parse_inner_url(image.file.url)
        image_list.append(image_template)
    return image_list


@transaction.atomic
def delete_image(_id):
    image = ExternalImage.objects.get(id=_id)
    path = image.file.path
    image.delete()
    os.remove(path)


@transaction.atomic
def query_model():
    model_list = list()
    models = ExternalModel.objects.all()
    for model in models:
        model_template = dict()
        model_template['id'] = model.id
        model_template['title'] = model.title
        model_template['description'] = model.description
        model_template['href'] = parse_inner_url(model.file.url)
        split_name = os.path.splitext(model_template['href'])
        ext = split_name[1]
        model_template['extension'] = ext
        model_list.append(model_template)
    return model_list


@transaction.atomic
def delete_model(_id):
    model = ExternalModel.objects.get(id=_id)
    path = model.file.path
    model.delete()
    os.remove(path)


POSSIBLE_RESOURCE = {
    'Music': {
        'name': 'Music', 'form': MusicForm, 'template': 'curator/resources/resources-music.html',
        'elements': query_music, 'delete': delete_music
    },
    'Image': {
        'name': 'Image', 'form': ImageForm, 'template': 'curator/resources/resources-images.html',
        'elements': query_image, 'delete': delete_image
    },
    'Model': {
        'name': 'Model', 'form': ModelForm, 'template': 'curator/resources/resources-models.html',
        'elements': query_model, 'delete': delete_model
    },
    'Video': {
        'name': 'Video', 'form': VideoForm, 'template': 'curator/resources/resources-video.html',
        'elements': query_video, 'delete': delete_video
    },
}
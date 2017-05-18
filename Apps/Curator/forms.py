#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import Textarea

from Apps.Curator.models.museums import UnityExhibit, VideoExhibit
from Apps.Curator.models.resources import ExternalImage, ExternalTemplate, ExternalMusic, ExternalModel, ExternalVideo

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


class CommonMeta:
    fields = ('title', 'description', 'file',)
    widgets = {
        'description': Textarea(attrs={'cols': 30, 'rows': 5}),
    }


class UnityExhibitMeta:
    fields = {'name', 'memory_to_allocate', 'data', 'javascript', 'memory'}
    labels = {'name': 'Name of exhibit',
              'memory_to_allocate': 'Unity TOTAL_MEMORY',
              'data': 'File exhibit.data',
              'javascript': 'File exhibit.js',
              'memory': 'File exhibit.mem'}


class VideoExhibitMeta:
    fields = {'name', 'video'}
    labels = {'name': 'Name of exhibit',
              'video': 'Video exhibit.(mp4/webm/ogg)'}


class NewExhibitForm(forms.ModelForm):
    field_order = ['name']


class UnityExhibitForm(forms.ModelForm):
    field_order = ['name', 'memory_to_allocate', 'data', 'javascript', 'memory']

    class Meta(UnityExhibitMeta):
        model = UnityExhibit


class VideoExhibitForm(forms.ModelForm):
    field_order = ['name', 'video']

    class Meta(VideoExhibitMeta):
        model = VideoExhibit


class TemplateForm(forms.ModelForm):
    class Meta(CommonMeta):
        model = ExternalTemplate


class MusicForm(forms.ModelForm):
    class Meta(CommonMeta):
        model = ExternalMusic


class ImageForm(forms.ModelForm):
    class Meta(CommonMeta):
        model = ExternalImage


class ModelForm(forms.ModelForm):
    class Meta(CommonMeta):
        model = ExternalModel


class VideoForm(forms.ModelForm):
    class Meta(CommonMeta):
        model = ExternalVideo

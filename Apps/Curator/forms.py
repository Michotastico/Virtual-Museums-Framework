#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import Textarea

from Apps.Curator.models.museums import UnityMuseum
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


class MuseumMeta:
    fields = {'name', 'memory_to_allocate', 'data', 'javascript', 'memory'}
    labels = {'name': 'Name of museum',
              'memory_to_allocate': 'Unity TOTAL_MEMORY',
              'data': 'File museum.data',
              'javascript': 'File museum.js',
              'memory': 'File museum.mem'}


class UnityMuseumForm(forms.ModelForm):
    field_order = ['name', 'memory_to_allocate', 'data', 'javascript', 'memory']

    class Meta(MuseumMeta):
        model = UnityMuseum


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

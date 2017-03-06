#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import Textarea

from Apps.Curator.models import ExternalImage, ExternalTemplate, ExternalMusic, ExternalModel

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


class CommonMeta:
    fields = ('title', 'description', 'file',)
    widgets = {
        'description': Textarea(attrs={'cols': 30, 'rows': 5}),
    }


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

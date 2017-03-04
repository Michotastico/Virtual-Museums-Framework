#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms

from Apps.Curator.models import ExternalImage, ExternalTemplate, ExternalMusic, ExternalModel

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


class TemplateForm(forms.ModelForm):
    class Meta:
        model = ExternalTemplate
        fields = ('title', 'description', 'document',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = ExternalImage
        fields = ('title', 'description', 'document',)


class MusicForm(forms.ModelForm):
    class Meta:
        model = ExternalMusic
        fields = ('title', 'description', 'document',)


class ModelForm(forms.ModelForm):
    class Meta:
        model = ExternalModel
        fields = ('title', 'description', 'document',)

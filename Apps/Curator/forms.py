#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms

from Apps.Curator.models import ExternalImage

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


class ImageForm(forms.ModelForm):
    class Meta:
        model = ExternalImage
        fields = ('title', 'description', 'document',)

from __future__ import unicode_literals

from django.db import models

# Create your models here.
from VirtualMuseumsFramework.settings import BASE_DIR


class ExternalFile(models.Model):
    title = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ExternalTemplate(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/template')


class ExternalImage(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/images')


class ExternalMusic(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/music')


class ExternalModel(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/models')

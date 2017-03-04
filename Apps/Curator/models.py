from __future__ import unicode_literals

from django.db import models
import os
from django.core.exceptions import ValidationError

# Create your models here.
from VirtualMuseumsFramework.settings import BASE_DIR


class ExternalFile(models.Model):
    title = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


def file_extension_validation(external_file, allowed_extensions):
    split_name = os.path.splitext(external_file.name)
    if len(split_name) > 2:
        raise ValidationError(u'Unsupported file extension.')

    ext = split_name[1]
    if not ext.lower() in allowed_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validator_template(external_file): file_extension_validation(external_file, ['.txt'])


class ExternalTemplate(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/template', validators=[validator_template])


def validator_image(external_file): file_extension_validation(external_file, ['.jpg', '.png'])


class ExternalImage(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/images', validators=[validator_image])


def validator_music(external_file): file_extension_validation(external_file, ['.mp3'])


class ExternalMusic(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/music', validators=[validator_music])


def validator_model(external_file): file_extension_validation(external_file, ['.off'])


class ExternalModel(ExternalFile):
    document = models.FileField(upload_to=BASE_DIR+'/static/external-content/models', validators=[validator_model])

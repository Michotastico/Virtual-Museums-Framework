from __future__ import unicode_literals

from django.db import models

from Apps.Curator.upload_manager import validator_template, rename_template, validator_image, rename_image, \
    validator_music, rename_music, validator_model, rename_model, rename_video, validator_video


class ExternalFile(models.Model):
    title = models.CharField(max_length=30, blank=False)
    description = models.CharField(max_length=255, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ExternalTemplate(ExternalFile):
    file = models.FileField(upload_to=rename_template, validators=[validator_template])


class ExternalMusic(ExternalFile):
    file = models.FileField(upload_to=rename_music, validators=[validator_music])


class ExternalImage(ExternalFile):
    file = models.FileField(upload_to=rename_image, validators=[validator_image])


class ExternalModel(ExternalFile):
    file = models.FileField(upload_to=rename_model, validators=[validator_model])


class ExternalVideo(ExternalFile):
    file = models.FileField(upload_to=rename_video, validators=[validator_video])

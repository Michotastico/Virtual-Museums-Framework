from __future__ import unicode_literals

import json

from django.db import models

from Apps.Curator.models.resources import ExternalMusic
from Apps.Curator.upload_manager import file_extension_validation, file_rename


class ExhibitType(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)


class Exhibit(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)
    visitors = models.PositiveIntegerField(default=0)
    exhibit_type = models.ForeignKey(ExhibitType, null=True)


def rename_unity_files(instance, filename): return file_rename(filename, '/static/external-content/unity-files')


def validator_data(external_file): file_extension_validation(external_file, ['.data'])


def validator_javascript(external_file): file_extension_validation(external_file, ['.js'])


def validator_memory(external_file): file_extension_validation(external_file, ['.mem'])


class UnityExhibit(Exhibit):
    memory_to_allocate = models.IntegerField(default=0)
    data = models.FileField(upload_to=rename_unity_files, validators=[validator_data])
    javascript = models.FileField(upload_to=rename_unity_files, validators=[validator_javascript])
    memory = models.FileField(upload_to=rename_unity_files, validators=[validator_memory])

    def save(self, *args, **kwargs):
        self.exhibit_type = ExhibitType.objects.get(name='Unity')
        super(UnityExhibit, self).save(*args, **kwargs)

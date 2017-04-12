from __future__ import unicode_literals

import json

from django.db import models

from Apps.Curator.models.resources import ExternalMusic
from Apps.Curator.upload_manager import file_extension_validation, file_rename


class Museum(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)
    visitors = models.IntegerField(default=0)


def rename_unity_files(instance, filename): return file_rename(filename, '/static/external-content/unity-files')


def validator_data(external_file): file_extension_validation(external_file, ['.data', '.datagz'])


def validator_javascript(external_file): file_extension_validation(external_file, ['.js', '.jsgz'])


def validator_memory(external_file): file_extension_validation(external_file, ['.mem', '.memgz'])


class UnityMuseum(Museum):
    data = models.FileField(upload_to=rename_unity_files, validators=[validator_data])
    javascript = models.FileField(upload_to=rename_unity_files, validators=[validator_javascript])
    memory = models.FileField(upload_to=rename_unity_files, validators=[validator_memory])


class Room(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)
    resources = models.TextField(default='{}')
    background_music = models.ForeignKey(ExternalMusic, null=True)
    published = models.BooleanField(default=False)
    popularity = models.IntegerField(default=0)

    north_room = models.ForeignKey("Room", null=True)
    south_room = models.ForeignKey("Room", null=True)
    west_room = models.ForeignKey("Room", null=True)
    east_room = models.ForeignKey("Room", null=True)

    def get_resources_as_dict(self):
        return json.loads(self.resources)

    def set_resources(self, resource_as_dict):
        self.resources = json.dumps(resource_as_dict)


'''
Resource JSON structure example:
{
    'width': number,
    'height': number,
    'lookup_image': url,
    'ground_layer': [{'type': ground/grass/stone/etc, 'x': number, 'y':number}],
    'object_layer': [{'type': image/model, 'id':number,
                    'orientation': N/S/W/E, 'x': number, 'y':number}],
    'vegetation_layer': [{'type': bush/tree/etc, 'x': number, 'y':number}]
}
'''
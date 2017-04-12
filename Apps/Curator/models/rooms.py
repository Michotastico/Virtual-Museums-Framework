from __future__ import unicode_literals

import json

from django.db import models

from Apps.Curator.models.resources import ExternalMusic


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
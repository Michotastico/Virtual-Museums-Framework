from __future__ import unicode_literals

import json

from django.db import models

from Apps.Curator.models.resources import ExternalMusic


class Room(models.Model):
    name = models.CharField(max_length=30, blank=False)
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

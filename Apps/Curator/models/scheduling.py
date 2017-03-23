from __future__ import unicode_literals

from django.db import models


class Exposition(models.Model):
    name = models.CharField(max_length=30, blank=False)
    status = models.BooleanField(default=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    main_room = models.ForeignKey("Room", null=True)

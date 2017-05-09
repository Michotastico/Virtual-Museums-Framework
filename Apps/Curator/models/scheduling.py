from __future__ import unicode_literals

from django.db import models


class Exhibition(models.Model):
    name = models.CharField(max_length=30, blank=False)
    status = models.BooleanField(default=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    museum = models.ForeignKey("Museum", null=True)

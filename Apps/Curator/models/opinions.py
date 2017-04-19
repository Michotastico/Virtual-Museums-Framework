from __future__ import unicode_literals

from django.db import models


class Opinion(models.Model):
    person_name = models.CharField(max_length=30, blank=False)
    opinion = models.TextField(blank=False)
    status = models.BooleanField(default=False)
    email = models.EmailField(blank=False)
    hash_key = models.TextField()
    validated = models.BooleanField(default=False)
    timeout = models.DateField(blank=False)

    museum = models.ForeignKey("Museum")

    @property
    def avatar(self):
        return "https://api.adorable.io/avatars/285/"+self.person_name+"@adorable.io"




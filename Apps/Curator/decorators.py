#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import user_passes_test

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in.
        http://garmoncheg.blogspot.cl/2012/06/users-groups-and-their-permissions-in.html
        on 19-04-2017"""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
            return False
    return user_passes_test(in_groups)

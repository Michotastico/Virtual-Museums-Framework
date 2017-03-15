#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os

from django.core.exceptions import ValidationError

from VirtualMuseumsFramework.settings import BASE_DIR

__author__ = "Michel Llorens"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "mllorens@dcc.uchile.cl"


def file_extension_validation(external_file, allowed_extensions):
    split_name = os.path.splitext(external_file.name)
    if len(split_name) > 2:
        raise ValidationError(u'Unsupported file extension.')

    ext = split_name[1]
    if not ext.lower() in allowed_extensions:
        raise ValidationError(u'Unsupported file extension.')


def file_rename(filename, path):
    split_name = filename.split('.')
    name = hashlib.sha1(split_name[0]).hexdigest()
    ext = split_name[-1]

    filename = "%s.%s" % (name, ext)
    return os.path.join(BASE_DIR+path, filename)


def validator_template(external_file): file_extension_validation(external_file, ['.txt'])


def rename_template(instance, filename): return file_rename(filename, '/static/external-content/template')


def validator_image(external_file): file_extension_validation(external_file, ['.jpg', '.png'])


def rename_image(instance, filename): return file_rename(filename, '/static/external-content/images')


def validator_music(external_file): file_extension_validation(external_file, ['.mp3'])


def rename_music(instance, filename): return file_rename(filename, '/static/external-content/music')


def validator_model(external_file): file_extension_validation(external_file, ['.off', '.obj'])


def rename_model(instance, filename): return file_rename(filename, '/static/external-content/models')
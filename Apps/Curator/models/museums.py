from __future__ import unicode_literals
from django.db import models
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


def rename_video_files(instance, filename): return file_rename(filename, '/static/external-content/video-files')


def validator_video(external_file): file_extension_validation(external_file, ['.mp4', '.webm', '.ogg'])


class VideoExhibit(Exhibit):
    video = models.FileField(upload_to=rename_video_files, validators=[validator_video])

    def save(self, *args, **kwargs):
        self.exhibit_type = ExhibitType.objects.get(name='Video')
        super(VideoExhibit, self).save(*args, **kwargs)


def rename_pdf_files(instance, filename): return file_rename(filename, '/static/external-content/pdf-files')


def validator_pdf(external_file): file_extension_validation(external_file, ['.pdf'])


class PDFExhibit(Exhibit):
    pdf = models.FileField(upload_to=rename_pdf_files, validators=[validator_pdf])

    def save(self, *args, **kwargs):
        self.exhibit_type = ExhibitType.objects.get(name='Pdf')
        super(PDFExhibit, self).save(*args, **kwargs)

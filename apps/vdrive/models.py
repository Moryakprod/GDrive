from django.db import models


from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Processing(models.Model):

    class Type(models.TextChoices):
        GDRIVE = 'GD', _('Gdrive type')
        GPHOTOS = 'GPH', _('Gphotos type')

    date = models.DateTimeField(verbose_name=_("creation date"), auto_now_add=True, null=True)
    source_type = models.CharField(choices=Type.choices, verbose_name=_("source of the file"), max_length=250, unique=True)


class VideoProcessing(models.Model):

    class Status(models.TextChoices):
        DOWNLOAD = 'DW', _('Download')
        WAITING = 'WT', _('Waiting to upload')
        IN_PROGRESS = 'IN_PR', _('In progress of uploading')
        ERROR_MESSAGE = 'ERROR_MESS', _('Error message')
        SUCCESSFUL_UPLOAD = 'SUCC_UP', _('Successfully Uploaded')

    processing = models.ForeignKey('vdrive.Processing', on_delete=models.CASCADE)
    source_id = models.CharField(verbose_name=_(" id of video in the source"),max_length=250, primary_key=True, unique=True,)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DOWNLOAD,)
    error_message_video = models.TextField(max_length=500, blank=True)
    youtube_id = models.CharField(verbose_name=_("id of youtube uploaded video"), max_length=250, unique=True,)
    youtube_link = models.URLField(verbose_name=_("link of the video from youtube"), max_length=250, unique=True)



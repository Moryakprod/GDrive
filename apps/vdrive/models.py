from django.contrib.auth import get_user_model
from django.db import models


from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Video(models.Model):
    class Type(models.TextChoices):
        GDRIVE = 'Google Drive', _('Gdrive type')
        GPHOTOS = 'Google Photos', _('Gphotos type')

    source_id = models.CharField(verbose_name=_(" id of video in the source"), max_length=250)
    name = models.CharField(verbose_name=_("name of the video"), max_length=250)
    source_type = models.CharField(choices=Type.choices, verbose_name=_("source of the file"), max_length=250)
    user = models.ForeignKey(get_user_model(), related_name='processings', on_delete=models.CASCADE)
    youtube_id = models.CharField(verbose_name=_("id of youtube uploaded video"), max_length=250, blank=True)


class Processing(models.Model):
    date = models.DateTimeField(verbose_name=_("creation date"), auto_now_add=True, null=True)


class VideoProcessing(models.Model):

    class Status(models.TextChoices):
        WAITING = 'waiting', _('Waiting to upload')
        DOWNLOAD = 'download', _('Download')
        UPLOAD = 'uploading', _('In progress of uploading')
        ERROR = 'errors', _('Error message')
        SUCCESS = 'success', _('Successfully Uploaded')

    processing = models.ForeignKey('Processing', on_delete=models.CASCADE, related_name='videos')
    videos = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='processings')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.WAITING,)
    error_message_video = models.TextField(blank=True)


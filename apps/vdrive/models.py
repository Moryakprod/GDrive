from django.contrib.auth import get_user_model
from django.db import models


from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Processing(models.Model):

    class Type(models.TextChoices):
        GDRIVE = 'GD', _('Gdrive type')
        GPHOTOS = 'GPH', _('Gphotos type')

    user = models.ForeignKey(get_user_model(), related_name='processings', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_("creation date"), auto_now_add=True, null=True)
    source_type = models.CharField(choices=Type.choices, verbose_name=_("source of the file"), max_length=250)


class VideoProcessing(models.Model):

    class Status(models.TextChoices):
        WAITING = 'waiting', _('Waiting to upload')
        DOWNLOAD = 'download', _('Download')
        UPLOAD = 'uploading', _('In progress of uploading')
        ERROR = 'errors', _('Error message')
        SUCCESS = 'success', _('Successfully Uploaded')


    processing = models.ForeignKey('Processing', on_delete=models.CASCADE, related_name='videos')
    source_id = models.CharField(verbose_name=_(" id of video in the source"), max_length=250)
    name = models.CharField(verbose_name=_("name of the video"), max_length=250)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING,)
    error_message_video = models.TextField(max_length=500, blank=True)
    youtube_id = models.CharField(verbose_name=_("id of youtube uploaded video"), max_length=250, blank=True)
    youtube_link = models.URLField(verbose_name=_("link of the video from youtube"), blank=True)



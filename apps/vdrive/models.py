from django.db import models

from django.template.defaultfilters import slugify
# Create your models here.


class Processing(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(
        verbose_name="creation date",
        auto_now_add=True, null=True
    )
    source_type = models.URLField(
        verbose_name="source of the file",
        max_length=250, unique=True
    )


class VideoProc(models.Model):

    Waiting = 'WT'
    InProgress = 'InPr'
    Error_Message = 'ErrorMes'
    Successful_Upload = 'SuccUp'
    STATUS_OF_VIDEO_UPLOADING = [
        (Waiting, 'Waiting to upload'),
        (InProgress, 'In progress of uploading'),
        (Error_Message, 'Error message'),
        (Successful_Upload, 'Successfully Uploaded'),
    ]

    proc_id = models.ForeignKey('vdrive.Processing', on_delete=models.CASCADE)
    source_id = models.AutoField(
        verbose_name=" id of video in the source",
        primary_key=True,
        unique=True
        )
    status_video = models.CharField(
        max_length=8,
        choices=STATUS_OF_VIDEO_UPLOADING,
        default=Waiting,
    )
    error_message_video = models.CharField(default="Error. Something went wrong", max_length=250)
    youtube_id = models.CharField(
        verbose_name=" id of youtube uploaded video",
        max_length=250,
        unique=True,
    )
    youtube_link = models.URLField(
        verbose_name="link of the video from youtube",
        max_length=250,
        unique=True
    )



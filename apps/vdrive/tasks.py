from datetime import time
from time import sleep

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import tempfile
from celery import shared_task
from googleapiclient.http import MediaIoBaseDownload
from django.contrib.auth.models import User
from celery import Celery
from celery.result import ResultBase
from apps.vdrive.models import VideoProcessing, Processing
print("Current temp directory:", tempfile.gettempdir())


@shared_task
def download(video_processing_pk):
    video_processing = VideoProcessing.objects.get(pk=video_processing_pk)
    user = video_processing.processing.user
    social = user.social_auth.filter(provider='google-oauth2').first()
    video_id = video_processing.source_id
    print(f'Downloading {video_id} for {user}')
    creds = Credentials(social.extra_data['access_token'])
    drive = build('drive', 'v3', credentials=creds)
    if video_id is None:
        video_processing.status = VideoProcessing.Status.ERROR
        msg = 'No Id provided'
        video_processing.error_message_video = msg
        video_processing.save()
        raise ValueError(msg)

    request = drive.files().get_media(fileId=video_id)
    with tempfile.NamedTemporaryFile(mode='w+b', delete=True) as f:
        video_processing.status = VideoProcessing.Status.DOWNLOAD
        video_processing.save()
        try:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk(1024)
                print("Download %d%%." % int(status.progress() * 100), video_id)

            video_processing.status = VideoProcessing.Status.UPLOAD
            video_processing.save()
        except Exception as e:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'Error: {e}'
            raise



        sleep(10)

        video_processing.status = VideoProcessing.Status.ERROR
        video_processing.error_message_video = 'No upload Implemented yet'
        video_processing.save()
        raise NotImplementedError

        video_processing.status = VideoProcessing.Status.SUCCESS
        video_processing.save()
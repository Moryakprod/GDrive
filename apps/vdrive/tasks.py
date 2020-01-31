import logging
import tempfile

from celery import shared_task

from django.contrib.auth import get_user_model
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .processing import download_from_gphotos, download_from_drive, upload_to_youtube
from .scan import scan_gphotos, scan_gdrive
from .utils import get_google_credentials
from apps.vdrive.models import VideoProcessing, Video, VideoScan


logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def process(video_processing_pk):
    video_processing = VideoProcessing.objects.get(pk=video_processing_pk)
    video = video_processing.video
    user = video.user
    video_id = video.source_id

    with tempfile.NamedTemporaryFile(mode='w+b', delete=True) as file_descriptor:
        print(f'Downloading {video_id} for {user}')
        if video_id is None:
            video_processing.status = VideoProcessing.Status.ERROR
            msg = 'No Id provided'
            video_processing.error_message_video = msg
            video_processing.save()
            raise ValueError(msg)

        video_processing.status = VideoProcessing.Status.DOWNLOAD
        video_processing.save()

        try:
            print(user, video_id, file_descriptor)
            if video_processing.video.source_type == Video.Type.GPHOTOS:
                download_from_gphotos(user, video_id, file_descriptor, video_processing)
            else:
                download_from_drive(user, video_id, file_descriptor, video_processing)

        except Exception as e:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'Error: {e}'
            video_processing.save()
            raise
        video_processing.status = VideoProcessing.Status.UPLOAD
        video_processing.save()

        try:
            youtube_id = upload_to_youtube(file_descriptor, user)
            video_processing.video.youtube_id = youtube_id
            video_processing.save()
            video_processing.status = VideoProcessing.Status.SUCCESS
            video_processing.save()
        except HttpError as er:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'An HTTP error occurred: {er.resp.status, er.content}'
            video_processing.save()
            raise


@shared_task
def scan_files(video_scan_id):
    video_scan = VideoScan.objects.get(id=video_scan_id)
    video_scan.status = VideoScan.Status.IN_PROGRESS
    video_scan.save()
    user = video_scan.user
    try:
        scan_gphotos(user)
        scan_gdrive(user)
    except Exception as e:
        video_scan.status = VideoScan.Status.ERROR
        video_scan.error_message = f'Error in scan: {e}'
        video_scan.save()

    video_scan.status = VideoScan.Status.SUCCESS
    video_scan.save()

@shared_task
def gdrive_del(id_source):
    video = Video.objects.get(source_id=id_source)
    user = video.user
    drive = build('drive', 'v3', credentials=get_google_credentials(user))
    drive.files().delete(fileId=id_source).execute()
    logger.info(f'Deleted file: { video.name }')
    video.status = Video.Status.DELETED
    video.save()

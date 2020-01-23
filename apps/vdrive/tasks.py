import logging
from datetime import time
import random
import time

from .utils import get_google_credentials
from googleapiclient.discovery import build
import tempfile
from celery import shared_task
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from apps.vdrive.models import VideoProcessing
from settings.base import RETRIABLE_STATUS_CODES, RETRIABLE_EXCEPTIONS, MAX_RETRIES

logger = logging.getLogger(__name__)


def upload_to_youtube(file_descriptor, youtube):
    body = {"snippet": {"title": "title", "description": "desc", "categoryId": "22"},
            "status": {"privacyStatus": "unlisted"}
            }

    logger.debug(file_descriptor.name)

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_descriptor.name, chunksize=-1, resumable=True)
    )

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Uploading file: %s", file_descriptor.name)
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    return response
                else:
                    raise ValueError("The upload failed with an unexpected response: %s" % response)
        except HttpError as er:
            if er.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (er.resp.status, er.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as er:
            error = "A retriable error occurred: %s" % er

        if error is not None:
            logger.debug(error)
            retry += 1
            if retry > MAX_RETRIES:
                raise ValueError("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            logger.debug("Sleeping %s seconds and then retrying...", sleep_seconds)
            time.sleep(sleep_seconds)


def download_from_drive(user, video_id, file_descriptor):
    credentials = get_google_credentials(user)
    drive = build('drive', 'v3', credentials=credentials)
    request = drive.files().get_media(fileId=video_id)
    downloader = MediaIoBaseDownload(file_descriptor, request)
    return downloader


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
            downloader = download_from_drive(user, video_id, file_descriptor)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                video_processing.progress = int(status.progress() * 100)
                video_processing.save()
                logger.info("Download %d, %s." % (video_processing.progress, video_id))
            video_processing.status = VideoProcessing.Status.UPLOAD
            video_processing.save()
        except Exception as e:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'Error: {e}'
            raise

        try:
            credentials = get_google_credentials(user)
            youtube = build("youtube", "v3", credentials=credentials)
            youtube_id = upload_to_youtube(file_descriptor, youtube)
            video_processing.video.youtube_id = youtube_id
            video_processing.save()
        except HttpError as er:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'An HTTP error occurred: {er.resp.status, er.content}'
            raise

        video_processing.status = VideoProcessing.Status.SUCCESS
        video_processing.save()

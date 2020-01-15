import logging
from datetime import time
from time import sleep
import random
import time

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import tempfile
from celery import shared_task
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from apps.vdrive.models import VideoProcessing, Processing
from settings.base import RETRIABLE_STATUS_CODES, RETRIABLE_EXCEPTIONS, MAX_RETRIES

logger = logging.getLogger(__name__)


def initialize_upload(youtube, f):
    body = dict(
        snippet=dict(
            title="title",
            description="desc",
            categoryId="22"
        ),
        status=dict(
            privacyStatus="unlisted"
        )
    )

    logger.debug(f.name)
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(f.name, chunksize=-1, resumable=True)
    )

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.debug("Uploading file...")
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
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                raise ValueError("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


@shared_task
def download(video_processing_pk):
    video_processing = VideoProcessing.objects.get(pk=video_processing_pk)
    user = video_processing.processing.user
    social = user.social_auth.filter(provider='google-oauth2').first()
    video_id = video_processing.source_id
    print(f'Downloading {video_id} for {user}')
    if video_id is None:
        video_processing.status = VideoProcessing.Status.ERROR
        msg = 'No Id provided'
        video_processing.error_message_video = msg
        video_processing.save()
        raise ValueError(msg)

    with tempfile.NamedTemporaryFile(mode='w+b', delete=True) as f:

        video_processing.status = VideoProcessing.Status.DOWNLOAD
        video_processing.save()
        try:
            creds = Credentials(social.extra_data['access_token'], social.extra_data['refresh_token'])
            drive = build('drive', 'v3', credentials=creds)
            request = drive.files().get_media(fileId=video_id)
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk(1024)
                video_processing.progress = int(status.progress() * 100)
                video_processing.save()
                print("Download %d%%." % int(status.progress() * 100), video_id)

            video_processing.status = VideoProcessing.Status.UPLOAD
            video_processing.save()
        except Exception as e:
            video_processing.status = VideoProcessing.Status.ERROR
            video_processing.error_message_video = f'Error: {e}'
            raise

        sleep(10)

        # video_processing.status = VideoProcessing.Status.ERROR
        # video_processing.error_message_video = 'No upload Implemented yet'
        # video_processing.save()
        # raise NotImplementedError

        try:
            youtube = build("youtube", "v3", credentials=creds)
            youtube_id = initialize_upload(youtube, f)
            video_processing.youtube_id = youtube_id
            video_processing.save()
        except HttpError as er:
            print("An HTTP error %d occurred:\n%s" % (er.resp.status, er.content))

        video_processing.status = VideoProcessing.Status.SUCCESS
        video_processing.save()

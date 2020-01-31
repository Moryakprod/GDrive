import logging
from datetime import time
import random
import time

import urllib.request

from django.contrib.auth import get_user_model
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from .utils import get_google_credentials
from settings.base import RETRIABLE_STATUS_CODES, RETRIABLE_EXCEPTIONS, MAX_RETRIES


logger = logging.getLogger(__name__)
User = get_user_model()


def download_from_drive(user, video_id, file_descriptor, video_processing):
    credentials = get_google_credentials(user)
    drive = build('drive', 'v3', credentials=credentials)
    request = drive.files().get_media(fileId=video_id)
    downloader = MediaIoBaseDownload(file_descriptor, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        video_processing.progress = int(status.progress() * 100)
        video_processing.save()
        logger.info("Download %d, %s." % (video_processing.progress, video_id))


def download_from_gphotos(user, video_id, file_descriptor, video_processing):
    credentials = get_google_credentials(user)
    photos = build('photoslibrary', 'v1', credentials=credentials)
    response = photos.mediaItems().get(mediaItemId=video_id).execute()
    base_url = response.get('baseUrl')
    if not base_url:
        raise ValueError('No video found')

    download_url = base_url + '=dv'

    with urllib.request.urlopen(download_url) as url_downloader:
        length = url_downloader.getheader('content-length')
        chunk_size = max(4096, int(length)//100)
        if not length:
            file_descriptor.write(url_downloader.read())
        else:
            while True:
                chunk = url_downloader.read(chunk_size)
                if not chunk:
                    break
                file_descriptor.write(chunk)


def upload_to_youtube(file_descriptor, user):
    body = {"snippet": {"title": "title", "description": "desc", "categoryId": "22"},
            "status": {"privacyStatus": "unlisted"}
            }

    logger.debug(file_descriptor.name)
    credentials = get_google_credentials(user)
    youtube = build("youtube", "v3", credentials=credentials)
    insert_request = youtube.videos().insert(
                                            part=",".join(body.keys()),
                                            body=body,
                                            media_body=MediaFileUpload(file_descriptor.name,
                                                                       chunksize=-1,
                                                                       resumable=True))

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
            logger.debug("Sleeping %f seconds and then retrying...", sleep_seconds)
            time.sleep(sleep_seconds)

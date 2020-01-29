import logging
from googleapiclient.discovery import build
import urllib.request
from hurry.filesize import size as sizer

from apps.vdrive.models import VideoProcessing, Processing, Video
from .utils import get_google_credentials


logger = logging.getLogger(__name__)


def scan_gdrive(user):
    drive = build('drive', 'v3', credentials=get_google_credentials(user))
    files_data = drive.files().list(q="mimeType contains 'video/'",
                                    spaces='drive',
                                    fields='files(id, name, size, thumbnailLink)'
                                    ).execute()
    logger.info(f'Found fies {files_data}')

    for item in files_data["files"]:
        video = Video.objects.get_or_create(source_type=Video.Type.GDRIVE,
                                            source_id=item['id'],
                                            user=user,
                                            defaults={
                                                'name': item['name'],
                                                'size': sizer(int(item['size'])),
                                                'thumbnail': item['thumbnailLink'],
                                            })
    return files_data['files']


def scan_gphotos(user):
    library = build('photoslibrary', 'v1', credentials=get_google_credentials(user))
    results = library.mediaItems().search().execute()
    logger.info(f'Found gphotos files {results}')
    items = results.get('mediaItems', [])
    for item in items:

        if not item['mimeType'].startswith('video'):
            continue
        base_url = item.get('baseUrl')

        if not base_url:
            logger.error(f'No base url for video {item}')
            continue

        download_url = base_url + '=dv'
        size = 0

        try:
            with urllib.request.urlopen(download_url) as url_downloader:
                size = sizer(int(url_downloader.getheader('content-length')))

        except Exception:
            logger.error(f'Error fetching size for video {item}')

        Video.objects.get_or_create(source_type=Video.Type.GPHOTOS,
                                    source_id=item['id'],
                                    user=user,
                                    defaults={
                                        'thumbnail': base_url + '=w300-h200',
                                        'name': item.get('filename', 'UNKNOWN'),
                                        'size': size,
                                    })
    return items
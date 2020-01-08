from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from apiclient.discovery import build
import tempfile
from googleapiclient.http import MediaIoBaseDownload


print("Current temp directory:", tempfile.gettempdir())
def download(id, user):
    social = user.social_auth.filter(provider='google-oauth2').first()
    creds = Credentials(social.extra_data['access_token'])
    drive = build('drive', 'v3', credentials=creds)
    if id is not None:
        request = drive.files().get_media(fileId=id)
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100), id)

    return
            # upload to youtube here

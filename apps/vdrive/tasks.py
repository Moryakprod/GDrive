from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from apiclient.discovery import build
import tempfile
from googleapiclient.http import MediaIoBaseDownload



def download(id, user):
    social = user.social_auth.filter(provider='google-oauth2').first()
    creds = Credentials(social.extra_data['access_token'])
    drive = build('drive', 'v3', credentials=creds)
    files_data = drive.files().list(q=("mimeType contains 'video/'"),
                                    spaces='drive',
                                    fields='files(id, name)').execute()
    print("Current temp directory:", tempfile.gettempdir())
    print(files_data)
    for file in files_data.get('files', []):
        print('File ID: %s' % file.get('id'))
        if id is not None and id in file.get('id'):
            print (drive.files().get_media(fileId=id))
            request = drive.files().get_media(fileId=id)
            print('request %s' % request)

            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))
    return
            # upload to youtube here

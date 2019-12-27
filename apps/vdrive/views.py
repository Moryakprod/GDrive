from time import sleep
from django.contrib.auth.mixins import LoginRequiredMixin
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView
from apiclient.discovery import build
import tempfile
from googleapiclient.http import MediaIoBaseDownload


class GDriveListView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/list.html'

    def get_files_list(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q=("mimeType contains 'video/'")).execute()
        print(files_data)
        return files_data['files']

    def process_from_google_drive(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q=("mimeType contains 'video/'"),
                                        spaces='drive',
                                        fields='files(id, name)').execute()
        for file in files_data.get('files', []):
            print('File ID: %s' %  file.get('id'))
            request = drive.files().get_media(fileId=file.get('id'))

            with tempfile.NamedTemporaryFile(mode='w+b') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 1))
                sleep(20)
        return
                # upload to youtube here

    def get_context_data(self):
        return {
            'files': self.get_files_list()
        }

from django.contrib.auth.mixins import LoginRequiredMixin
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView
from apiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GDriveListView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/list.html'

    def get_files_list(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        request = drive.files().get_media(fileId='1FlF-ko_30BcGt_bhmO1jFxgfU-voHzLH')
        # downloading to 1.mp4 file
        with open("1.mp4", 'wb+') as fd:
            downloader = MediaIoBaseDownload(fd, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
    def get_context_data(self):
        return {
            'files': self.get_files_list()
        }

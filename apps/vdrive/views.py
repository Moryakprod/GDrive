from django.contrib.auth.mixins import LoginRequiredMixin
from apiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView
from apps.vdrive.tasks import download



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

    def get_context_data(self):
        return {
            'files': self.get_files_list()
        }


class Downloader(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/download.html'

    def get_files_list(self):
        user = self.request.user
        id = '0BxqwaD57DT2fQ29oWkJTdWU5dFU'
        start_download = download(id=id, user=user)
        print('Start dow', download(id=id, user=user))
        return start_download()

    def get_context_data(self):
        return{
            self.get_files_list()
        }

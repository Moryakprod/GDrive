from django.contrib.auth.mixins import LoginRequiredMixin
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView


class GDriveListView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/list.html'

    def get_files_list(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list().execute()
        print(files_data)
        return files_data['files']

    def get_context_data(self):
        return {
            'files': self.get_files_list()
        }
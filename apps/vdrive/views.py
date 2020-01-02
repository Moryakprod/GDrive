from django.contrib.auth.mixins import LoginRequiredMixin
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView, UpdateView
from apps.vdrive.models import VideoProcessing, Processing
from django.shortcuts import render
from django.urls import reverse


class GDriveListView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/list.html'

    def get_files_list(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q="mimeType='video/mp4'").execute()
        print(files_data)
        return files_data['files']

    def get_context_data(self):
        return {
            'files': self.get_files_list()
        }


class UserListView(ListView):
    model = Processing
    template_name = 'vdrive/imports_list.html'

from django.contrib.auth.mixins import LoginRequiredMixin
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView, FormView
from django.views import View
from django.shortcuts import render
from django import forms


class GDriveListView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/form.html'

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


# class MyFormView(LoginRequiredMixin, FormView):
#     template_name  = 'vdrive/form.html'
#     form_class = MyForm
#     success_url = '/'


class MyForm(forms):
    if __name__ == '__main__':
        lsit = forms

    def clean_list(self):
        value = self.data.get()


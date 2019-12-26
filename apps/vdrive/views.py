from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.views.generic import TemplateView, FormView
from django.views import View
from django.shortcuts import render
from django import forms



class MyForm(forms.Form):
    # template_name = 'vdrive/form.html'
    # files = forms.CharField()
    # cb = forms.BooleanField()
    success_url = '/'
    def __init__(self, *args, videos=None, **kwargs):
        super().__init__(*args, **kwargs)
        for video in videos:
            field_name = '%s' % video['name']
            self.fields[field_name] = forms.BooleanField(required=False)
            self.initial[field_name] = True


class MyView(FormView):
    template_name = 'vdrive/form.html'
    form_class = MyForm


    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""

        kwargs = super().get_form_kwargs()
        kwargs['videos'] = self.get_files_list()
        return kwargs


    def get_files_list(self):
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q="mimeType='video/mp4'").execute()
        print(files_data)
        return files_data['files']


    # def get_context_data(self):
    #     return {
    #         'files': self.post()
    #     }

    # def get(self, request, *args, **kwargs):=
    #     return HttpRequest.FILES()

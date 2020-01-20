import logging

from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, FormView, UpdateView
from apps.vdrive.tasks import download
from apps.vdrive.models import VideoProcessing, Processing, Video
from django.shortcuts import render
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


class GDriveListForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for video in user.videos.all():
            field_name = video.name
            field_id = video.id
            self.fields[field_id] = forms.BooleanField(required=False, label=field_name)
            self.initial[field_id] = False


class GDriveListView(LoginRequiredMixin, FormView):
    template_name = 'vdrive/list.html'
    form_class = GDriveListForm
    success_url = reverse_lazy('vdrive:imports_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_files_list(self):
        user = self.request.user
        print(user)
        social = user.social_auth.filter(provider='google-oauth2').first()
        print(social)
        creds = Credentials(social.extra_data['access_token'], social.extra_data['refresh_token'],
                            token_uri=settings.TOKEN_URI, client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET)
        print(creds)
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q="mimeType contains 'video/'", spaces='drive',
                                        fields='files(id, name)').execute()
        logger.info(f'Found fies {files_data}')
        for item in files_data["files"]:
            video = Video.objects.get_or_create(source_id=item['id'], name=item['name'],
                                                user=user, source_type=Video.Type.GDRIVE)
        return files_data['files']

    def form_valid(self, form):
        data = list(form.data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        processing = Processing.objects.create()
        for video_id in videos:
            video_processing = VideoProcessing.objects.create(video_id=video_id, processing=processing)
            video_processing.save()
            download.delay(video_processing.pk)
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'vdrive/imports_list.html'
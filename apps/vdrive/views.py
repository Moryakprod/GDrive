import logging

from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, FormView, UpdateView
from apps.vdrive.tasks import download
from apps.vdrive.models import VideoProcessing, Processing
from django.shortcuts import render
from django.contrib.auth.models import User
from .utils import get_google_credentials


logger = logging.getLogger(__name__)


class GDriveListForm(forms.Form):

    def __init__(self, *args, videos=None, **kwargs):
        super().__init__(*args, **kwargs)
        for video in videos:
            field_name = video['name']
            field_id = video['id']
            self.fields[field_id] = forms.BooleanField(required=False, label=field_name)
            self.initial[field_id] = False


class GDriveListView(LoginRequiredMixin, FormView):
    template_name = 'vdrive/list.html'
    form_class = GDriveListForm
    success_url = reverse_lazy('vdrive:imports_list')

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""

        kwargs = super().get_form_kwargs()
        kwargs['videos'] = self.get_files_list()
        return kwargs

    def get_files_list(self):
        user = self.request.user
        drive = build('drive', 'v3', credentials=get_google_credentials(user))
        files_data = drive.files().list(q=("mimeType contains 'video/'"),
                                        spaces='drive',
                                        fields='files(id, name)').execute()

        logger.info(f'Found fies {files_data}')
        return files_data['files']

    def form_valid(self, form):
        data = list(form.data)
        print(data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        processing = Processing.objects.create(user=self.request.user, source_type=Processing.Type.GDRIVE)
        for video_id in videos:
            video_processing = VideoProcessing.objects.create(source_id=video_id, processing=processing)
            download.delay(video_processing.pk)

        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = Processing
    template_name = 'vdrive/imports_list.html'

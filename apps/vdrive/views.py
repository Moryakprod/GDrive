import logging

from .utils import get_google_credentials
from googleapiclient.discovery import build
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView
from apps.vdrive.tasks import download
from apps.vdrive.models import VideoProcessing, Processing, Video


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
        drive = build('drive', 'v3', credentials=get_google_credentials(user))
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

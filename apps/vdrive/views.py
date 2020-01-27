import logging

from django import forms
from django.db.transaction import on_commit
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView

from googleapiclient.discovery import build

from apps.vdrive.tasks import process
from apps.vdrive.models import VideoProcessing, Processing, Video
from .utils import get_google_credentials


logger = logging.getLogger(__name__)


class GDriveListForm(forms.Form):
    def __init__(self, *args, videos=None, **kwargs):
        super().__init__(*args, **kwargs)
        for video in videos:
            field_name = video.name
            field_id = video.id
            self.fields[field_id] = forms.BooleanField(required=False, label=field_name)
            self.initial[field_id] = False


class GDriveListView(LoginRequiredMixin, FormView):
    template_name = 'vdrive/list.html'
    form_class = GDriveListForm
    success_url = reverse_lazy('vdrive:imports_list')

    def get_form_kwargs(self):
        self.get_files_list()
        self.get_files_list_gphotos()
        kwargs = super().get_form_kwargs()
        kwargs['videos'] = self.get_videos()
        return kwargs

    def get_videos(self):
        return self.request.user.videos\
            .exclude(processings__status=VideoProcessing.Status.SUCCESS)\
            .exclude(status=Video.Status.DELETED)

    def get_context_data(self, **kwargs):
        context = super(GDriveListView, self).get_context_data(**kwargs)
        context['videos'] = self.get_videos()
        return context

    def get_files_list(self):
        user = self.request.user
        drive = build('drive', 'v3', credentials=get_google_credentials(user))
        files_data = drive.files().list(q="mimeType contains 'video/'",
                                        spaces='drive',
                                        fields='files(id, name, size, thumbnailLink)'
                                        ).execute()
        logger.info(f'Found fies {files_data}')

        for item in files_data["files"]:
            video = Video.objects.get_or_create(source_id=item['id'],
                                                user=user,
                                                source_type=Video.Type.GDRIVE,
                                                defaults={
                                                    'name': item['name'],
                                                    'thumbnail': item.get('thumbnailLink', ''),
                                                    'size': item['size']
                                                })
        return files_data['files']

    def get_files_list_gphotos(self):
        user = self.request.user
        library = build('photoslibrary', 'v1', credentials=get_google_credentials(user))
        results = library.mediaItems().list().execute()
        logger.info(f'Found gphotos files {results}')
        items = results.get('mediaItems', [])
        for item in items:
            print(item['mimeType'], item['filename'])
            if not item['mimeType'].startswith('video'):
                continue
            Video.objects.get_or_create(source_type=Video.Type.GPHOTOS, source_id=item['id'],
                                        user=self.request.user,
                                        defaults={
                                            'name': item.get('filename', 'UNKNOWN')
                                        }
                                        )
        return items

    def form_valid(self, form):
        data = list(form.data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        processing = Processing.objects.create()
        for video_id in videos:
            video_processing = VideoProcessing.objects.create(video_id=video_id, processing=processing)
            video_processing.save()
            on_commit(lambda: process.delay(video_processing.pk))
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = Processing
    template_name = 'vdrive/imports_list.html'


class DelListForm(forms.Form):
    def __init__(self, *args, user=None,  **kwargs):
        super().__init__(*args, **kwargs)
        for video in user.videos.filter(processings__status='success'):
            field_name = video.name
            field_id = video.id
            self.fields[field_id] = forms.BooleanField(required=False,
                                                       label=field_name)
            self.initial[field_id] = False


class DeleteListView(LoginRequiredMixin, FormView):
    template_name = 'vdrive/delete_list.html'
    form_class = DelListForm
    success_url = reverse_lazy('vdrive:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_files_list(self):
        return

    def form_valid(self, form):
        data = list(form.data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        drive = build('drive', 'v3', credentials=get_google_credentials(self.request.user))
        for video_id in videos:
            id = Video.objects.get(id=video_id)
            id_source = id.source_id
            drive.files().delete(fileId=id_source).execute()
            logger.info(f'Deleted file: {id}')
            id.status = Video.Status.DELETED
            id.save()
        return super().form_valid(form)
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


class GDriveListForm(forms.Form):
    success_url = reverse_lazy('vdrive:list')

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
    success_url = reverse_lazy('vdrive:list')

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""

        kwargs = super().get_form_kwargs()
        kwargs['videos'] = self.get_files_list()
        return kwargs

    def get_files_list(self):
        user = User.objects.filter().last()
        social = user.social_auth.filter(provider='google-oauth2').first()
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q=("mimeType contains 'video/'"),
                                        spaces='drive',
                                        fields='files(id, name)').execute()
        return files_data['files']

    def form_valid(self, form):
        data = list(form.data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        for id in videos:
            download.apply_async(args=[id], countdown=2)
        return super().form_valid(form)


class DownloaderView(LoginRequiredMixin, TemplateView):
    template_name = 'vdrive/download.html'


    def get(request, id):
        download(id)
        return render(request, 'vdrive/download.html')


class UserListView(ListView):
    model = Processing
    template_name = 'vdrive/imports_list.html'

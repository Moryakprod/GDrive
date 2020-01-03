from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from apps.vdrive.models import Processing
from django.contrib.auth.mixins import LoginRequiredMixin


class GDriveListForm(forms.Form):
    success_url = reverse_lazy('vdrive:list')

    def __init__(self, *args, videos=None, **kwargs):
        super().__init__(*args, **kwargs)
        for video in videos:
            field_name = video['name']
            field_id = video['id']
            self.fields[field_id] = forms.BooleanField(required=False, label=field_name)
            self.initial[field_id] = True


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
        user = self.request.user
        social = user.social_auth.get(provider='google-oauth2')
        creds = Credentials(social.extra_data['access_token'])
        drive = build('drive', 'v3', credentials=creds)
        files_data = drive.files().list(q=("mimeType contains 'video/'")).execute()
        return files_data['files']

    def form_valid(self, form):
        data = list(form.data)
        videos = [field for field in data if field != 'csrfmiddlewaretoken']
        print(videos)
        return super().form_valid(form)


class UserListView(ListView):
    model = Processing
    template_name = 'vdrive/imports_list.html'

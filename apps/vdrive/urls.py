from django.contrib import admin
from django.urls import path, include, re_path
from apps.vdrive.views import GDriveListView

app_name = 'login'

urlpatterns = [
    path('', GDriveListView.as_view(), name='list'),
]

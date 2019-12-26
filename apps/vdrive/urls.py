from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic import TemplateView

app_name = 'login'

urlpatterns = [
    re_path(r'^$', views.GDriveListView.as_view()),
    re_path(r'^form/$', views.MyFormView.as_view())
]

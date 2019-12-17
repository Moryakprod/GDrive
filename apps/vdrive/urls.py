from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import TemplateView

app_name = 'login'

urlpatterns = [
    path('', views.GDriveListView.as_view()),
]

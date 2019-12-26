from django.contrib import admin
from django.urls import path, include, re_path
from apps.vdrive.views import MyView
from django.views.generic import TemplateView

app_name = 'login'

urlpatterns = [
    # path('', ),
    path('form/', MyView.as_view()),
]

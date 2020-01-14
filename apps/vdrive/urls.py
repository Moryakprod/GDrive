from django.contrib import admin
from django.urls import path, include
from . import views, tasks
from django.views.generic import TemplateView
from . import views
from django.urls import path, include, re_path
from apps.vdrive.views import GDriveListView


app_name = 'login'

urlpatterns = [

    path('', views.GDriveListView.as_view()),
    # path('download/<str:id>', views.DownloaderView.as_view(), name='Downloader'),
    path('imports_list/', views.UserListView.as_view()),

    path('', GDriveListView.as_view(), name='list'),
    path('imports_list/', views.UserListView.as_view(), name='imports_list'),

]

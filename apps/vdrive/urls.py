from . import views
from django.urls import path
from apps.vdrive.views import GDriveListView


app_name = 'login'

urlpatterns = [

    path('', views.GDriveListView.as_view()),
    path('imports_list/', views.UserListView.as_view()),

    path('', GDriveListView.as_view(), name='list'),
    path('imports_list/', views.UserListView.as_view(), name='imports_list'),

]

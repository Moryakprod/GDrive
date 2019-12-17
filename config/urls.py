"""vdrive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import re_path, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, re_path
from django.contrib import admin

from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Remove default django '/' site_url to hide 'View Site' button in Admin header
admin.site.site_url = None

schema_view = get_schema_view(
    openapi.Info(
        title='vdrive API',
        default_version='v1',
        description='Vdrive for import from google to youtube',
        contact=openapi.Contact(email="contact@atomcream.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    #API
    re_path(r'^api/v1/api_auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/v1/auth/', include('apps.authentication.urls', namespace='authentication')),
    re_path(r'^api/v1/vdrive/', include('apps.vdrive.urls', namespace='vdrive')),

    # Docs
    re_path(r'^api/v1/docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(
        r'^api/v1/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^api/v1/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
]

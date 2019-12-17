from django.conf.urls import re_path

from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import (
    obtain_jwt_token, refresh_jwt_token, verify_jwt_token,
)

from .views import UserViewSet


app_name = 'authentication'
router = DefaultRouter()  # pylint: disable=invalid-name

router.register(r'', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/', obtain_jwt_token, name='login'),
    re_path(r'^token_refresh/', refresh_jwt_token, name='token-refresh'),
    re_path(r'^token_verify/', verify_jwt_token, name='token-verify')
]

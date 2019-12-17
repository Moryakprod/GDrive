from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin


from apps.utils.tasks import send_notification_user_created, send_password_restore_link
from .jwt_utils import response_with_token
from .models import User
from .permissions import IsAdminOrOwnUserObjectAccess
from .serializers import BasePasswordSerializer, HashSerializer, RestorePasswordSerializer, \
    UserSerializer, UpdatePasswordSerializer


class UserViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  UpdateModelMixin,
                  GenericViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.filter(is_staff=False, is_superuser=False)
    permission_classes = (IsAdminOrOwnUserObjectAccess,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        passwords = BasePasswordSerializer(data=request.data)
        passwords.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_instance = User.objects.get(id=serializer.data.get('id'))
        user_instance.set_password(request.data.get('password'))
        user_instance.save()
        response = response_with_token(user_instance, serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = response_with_token(instance, serializer.data)
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrOwnUserObjectAccess])
    def update_password(self, request, pk=None):
        user = self.get_object()
        serializer = UpdatePasswordSerializer(data=request.data, context=user)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.data['password'])
            user.save()
            user_data = response_with_token(user, UserSerializer(user).data)
            response = {**user_data, 'detail': [_('Password is successfully updated!')]}
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def confirm_email(self, request):
        serializer = HashSerializer(
            data={'hash': request.query_params.get('hash')}, cache_key_action='email_confirmation_'
        )
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(id=serializer.validated_data.get('hash').get('id'))
            user.is_confirmed_email = True
            user.save()
            send_notification_user_created.delay(user.id)
            return Response({'is_confirmed_email': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def restore_password_link(self, request, pk=None):
        try:
            user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            return Response(
                {'email': [_('Email is invalid')]},
                status=status.HTTP_404_NOT_FOUND
            )
        # TODO: add celery tasks handling
        send_password_restore_link.delay(user.id)
        return Response({'detail': [_('Email is sent!')]}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def restore_password(self, request, pk=None):
        data = dict.copy(request.data)
        data.update({'hash': request.query_params.get('hash')})
        serializer = RestorePasswordSerializer(data=data, cache_key_action='password_restore_')
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(id=serializer.validated_data.get('hash').get('id'))
            user.set_password(serializer.validated_data.get('password'))
            user.save()
            user_data = response_with_token(user, UserSerializer(user).data)
            response = {**user_data, 'detail': [_('Password is successfully restored!')]}
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

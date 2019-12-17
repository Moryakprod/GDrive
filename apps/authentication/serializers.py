from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, validators

from apps.utils.communication import decode_base64_to_dict
from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'get_full_name', 'is_active', 'last_login',
            'email', 'is_staff', 'date_joined',
        )
        read_only_fields = ('last_login', 'date_joined', 'is_staff', 'id', 'is_staff',)


class BasePasswordSerializer(serializers.Serializer):
    """
    Serializer for update password API.
    """
    password = serializers.CharField(required=True, min_length=8)
    password_check = serializers.CharField(required=True, min_length=8)

    def validate(self, data):
        """Validation for checking password match."""
        if data['password'] != data['password_check']:
            raise serializers.ValidationError({'password_check': _("Passwords don't match!")})
        return data


class UpdatePasswordSerializer(BasePasswordSerializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """ self.context - user instance """
        if not self.context.check_password(value):
            raise serializers.ValidationError(_('Current password is incorrect'))
        return value

    def validate(self, data):
        if data['old_password'] == data['password']:
            raise serializers.ValidationError(
            {'old_password': _('New password cannot be the same as your old password')}
        )
        return data


class HashSerializer(serializers.Serializer):
    """
    Serializer for hash validation.
    """
    hash = serializers.CharField(required=True)

    def __init__(self, cache_key_action=None, *args, **kwargs):
        self.cache_key_action = cache_key_action
        super().__init__(self, *args, **kwargs)

    def validate_hash(self, value):
        decoded_data = decode_base64_to_dict(value, serializers.ValidationError(_(
            'Link is invalid. Please, try again.'
        )))
        if self.cache_key_action is not None:
            cache_key = f"{self.cache_key_action}{decoded_data.get('id')}"
            data_from_cache = cache.get(cache_key)
            if data_from_cache != decoded_data:
                raise serializers.ValidationError(
                    _('Email confirmation link is not valid. Please try again.')
                )
            cache.delete(cache_key)
        return decoded_data


class RestorePasswordSerializer(BasePasswordSerializer, HashSerializer):
    pass

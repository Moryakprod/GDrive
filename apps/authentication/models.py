from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin,
)
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _


from apps.utils.tasks import send_email_confirmation_link
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    """

    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    email = models.EmailField(_('Email'), unique=True)
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    is_staff = models.BooleanField(_('Is staff'), default=False)
    is_confirmed_email = models.BooleanField(_('Is confirm email'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        """
        Returns user's concatenated first and last name
        """
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __str__(self):
        return self.get_full_name()

    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(User, self).save(*args, **kwargs)

        if is_new:
            transaction.on_commit(lambda: send_email_confirmation_link.delay(self.id))

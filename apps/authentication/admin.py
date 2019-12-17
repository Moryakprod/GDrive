from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User
from .forms import UserCreationForm, UserChangeForm


# Remove default django Group model
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_confirmed_email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_staff',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2',)
            }
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm

    empty_value_display = 'unknown'
    list_display = ('__str__', 'email', 'date_joined', 'is_staff',)
    list_display_links = ('__str__', 'email',)
    list_filter = ('is_staff', 'date_joined',)

    readonly_fields = ('last_login', 'date_joined', 'is_confirmed_email',)
    search_fields = ('first_name', 'last_name', 'email',)
    ordering = ('email',)

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy

from authenticate.models import ExpiredToken, ExpiredTokenProxy, PasswordlessUser


# Register your models here.
@admin.register(PasswordlessUser)
class PasswordlessUserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("email", "username", "phone_number", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff")
    fieldsets = (
        ("Information", {"fields": ("username", "email", "phone_number", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "last_login",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = ((None, {"fields": ("phone_number", "email")}),)
    search_fields = ("email", "phone_number")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if is_superuser:
            form.base_fields["is_superuser"].disabled = True
        return form


User = get_user_model()


class ExpiredTokenAdmin(TokenAdmin):
    list_display = ("key", "user", "created", "expired")
    list_filter = ("expired",)
    fields = ("user",)

    def get_object(self, request, object_id, from_field=None):
        """
        Map from User ID to matching Token.
        """
        queryset = self.get_queryset(request)
        field = User._meta.pk
        try:
            object_id = field.to_python(object_id)
            user = User.objects.get(**{field.name: object_id})
            return queryset.get(user=user)
        except (
            queryset.model.DoesNotExist,
            User.DoesNotExist,
            ValidationError,
            ValueError,
        ):
            return None

    def delete_model(self, request, obj):
        # Map back to actual Token, since delete() uses pk.
        token = ExpiredToken.objects.get(key=obj.key)
        return super().delete_model(request, token)


admin.site.register(ExpiredTokenProxy, ExpiredTokenAdmin)
if "rest_framework.authtoken" in settings.INSTALLED_APPS:
    admin.site.unregister(TokenProxy)

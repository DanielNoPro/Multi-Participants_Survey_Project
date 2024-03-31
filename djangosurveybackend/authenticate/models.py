from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from drfpasswordless.settings import api_settings
from rest_framework.authtoken.models import Token

from authenticate.manager import PasswordlessUserAccountManager

TIMEDELTA = timezone.timedelta(
    seconds=float(api_settings.PASSWORDLESS_TOKEN_EXPIRE_TIME) * 10
)


# Create your models here.
class PasswordlessUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Please enter a valid phone number"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = PasswordlessUserAccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone_number"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


def get_expired_default_time():
    return timezone.now() + TIMEDELTA


class ExpiredToken(Token):
    expired = models.DateTimeField(default=get_expired_default_time)

    class Meta:
        abstract = "authenticate" not in settings.INSTALLED_APPS
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def is_expired(self):
        return timezone.now() > self.expired

    def refresh_expiration(self):
        self.created = timezone.now()
        self.expired = self.created + TIMEDELTA
        # self.key = self.generate_key()
        return super().save()


class ExpiredTokenProxy(ExpiredToken):
    @property
    def pk(self):
        return self.user_id

    class Meta:
        proxy = "authenticate" in settings.INSTALLED_APPS
        abstract = "authenticate" not in settings.INSTALLED_APPS
        verbose_name = "Token"

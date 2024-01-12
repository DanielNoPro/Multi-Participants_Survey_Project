"""Containers module."""

from dependency_injector import containers, providers
from django.conf import settings
from . import services


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    mail_service = providers.Factory(
        services.MailService,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS
    )

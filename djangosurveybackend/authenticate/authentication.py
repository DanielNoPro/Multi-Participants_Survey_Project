import base64
import json
import logging
import os.path

from django.core.mail import get_connection, send_mail
from django.template import loader
from django.utils.module_loading import import_string
from drfpasswordless.settings import api_settings
from drfpasswordless.utils import inject_template_context
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from authenticate.models import ExpiredToken
from surveybackend import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    keyword = "Token"
    model = ExpiredToken

    def authenticate_credentials(self, key):
        _, token = super().authenticate_credentials(key)

        if not isinstance(token, self.model):
            raise AuthenticationFailed("Invalid token type")

        if token.is_expired():
            raise AuthenticationFailed("Token has expired")

        return token.user, token


def create_authentication_token(user):
    token, created = ExpiredToken.objects.get_or_create(user=user)
    if not created:
        token.refresh_expiration()
    return token, created


def create_auth_claim(user, email_token, **kwargs):
    return {"email": user.email, "token": email_token.key}


def send_email_with_callback_magic_link(user, email_token, **kwargs):
    redirect_link_creator = import_string(settings.PASSWORDLESS_AUTH_LINK_CREATOR)
    claim_json_creator = import_string(settings.PASSWORDLESS_AUTH_CLAIM_CREATOR)
    redirect_link = redirect_link_creator(user, **kwargs)
    claim_json = claim_json_creator(user, email_token, **kwargs)
    claim = json.dumps(claim_json, default=str)
    base64_claim = base64.b64encode(claim.encode("ascii")).decode("ascii")
    email_token.key = os.path.join(redirect_link, base64_claim)
    try:
        # Get email subject and message
        email_subject = kwargs.get(
            "email_subject", api_settings.PASSWORDLESS_EMAIL_SUBJECT
        )
        email_plaintext = kwargs.get(
            "email_plaintext", api_settings.PASSWORDLESS_EMAIL_PLAINTEXT_MESSAGE
        )
        email_html = kwargs.get(
            "email_html", api_settings.PASSWORDLESS_EMAIL_TOKEN_HTML_TEMPLATE_NAME
        )

        # Inject context if user specifies.
        context = inject_template_context(
            {
                "callback_token": email_token.key,
            }
        )
        html_message = loader.render_to_string(
            email_html,
            context,
        )
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        ) as connection:
            send_mail(
                email_subject,
                email_plaintext % email_token.key,
                api_settings.PASSWORDLESS_EMAIL_NOREPLY_ADDRESS,
                [getattr(user, api_settings.PASSWORDLESS_USER_EMAIL_FIELD_NAME)],
                fail_silently=False,
                html_message=html_message,
                connection=connection,
            )

        return True
    except Exception as e:
        logging.error(
            "Failed to send token email to user: %d."
            "Possibly no email on user object. Email entered was %s"
            % (user.id, getattr(user, api_settings.PASSWORDLESS_USER_EMAIL_FIELD_NAME))
        )
        logging.error(e)
        return False

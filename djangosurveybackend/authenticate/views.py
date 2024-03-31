import base64
import json
import logging

from django.utils.module_loading import import_string
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainAuthTokenFromCallbackToken
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@authentication_classes([])
@permission_classes([AllowAny])
class ObtainAuthTokenFromCallbackRedirectToken(ObtainAuthTokenFromCallbackToken):
    def post(self, request, *args, **kwargs):
        request_data = json.loads(base64.b64decode(request.data.get("token")))
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
            (token, _) = token_creator(user)

            if token:
                TokenSerializer = import_string(
                    api_settings.PASSWORDLESS_AUTH_TOKEN_SERIALIZER
                )
                token_serializer = TokenSerializer(
                    data=token.__dict__, partial=True, context={"request": request}
                )
                if token_serializer.is_valid():
                    # Return our key for consumption.
                    return Response(token_serializer.data, status=status.HTTP_200_OK)
        else:
            logging.error(
                "Couldn't log in unknown user. Errors on serializer: {}".format(
                    serializer.error_messages
                )
            )
        return Response(
            {"detail": "Couldn't log you in. Try again later."},
            status=status.HTTP_400_BAD_REQUEST,
        )

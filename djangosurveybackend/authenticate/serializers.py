from rest_framework import serializers

from authenticate.models import PasswordlessUser


class PasswordlessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordlessUser
        fields = "__all__"

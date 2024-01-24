from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CoreTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.get_username()
        if hasattr(token, 'email'):
            token["email"] = str(user.email)
        if hasattr(token, 'phone_number'):
            token["phone_number"] = str(user.phone_number)
        if hasattr(token, 'first_name'):
            token["first_name"] = str(user.first_name)
        if hasattr(token, 'last_name'):
            token["last_name"] = str(user.last_name)

        return token

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CoreTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.get_username()
        token["email"] = str(user.email)
        token["first_name"] = str(user.first_name)
        token["last_name"] = str(user.last_name)

        return token

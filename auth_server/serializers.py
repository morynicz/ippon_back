from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenSerializer, cls).get_token(user)
        # token['expires_at'] = 1234

        return token

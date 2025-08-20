from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import User


class Neo4jJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            if not user_id:
                raise InvalidToken(
                    "Token contained no recognizable user identification"
                )

            try:
                neo4j_user = User.nodes.get(uid=user_id)

                class DjangoUserProxy:
                    def __init__(self, neo4j_user):
                        self.id = neo4j_user.uid
                        self.is_authenticated = True
                        self.is_active = neo4j_user.is_active

                    @property
                    def pk(self):
                        return self.id

                django_user = DjangoUserProxy(neo4j_user)

                return django_user, neo4j_user

            except User.DoesNotExist:
                raise InvalidToken("User not found")

        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        django_user, neo4j_user = self.get_user(validated_token)

        request.neo4j_user = neo4j_user

        return (django_user, validated_token)


def create_jwt_token(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    class DummyUser:
        def __init__(self, uid):
            self.id = uid
            self.pk = uid

    dummy_user = DummyUser(user.uid)
    refresh = RefreshToken.for_user(dummy_user)

    # Add custom claims
    refresh["user_id"] = user.uid
    refresh["email"] = user.email
    refresh["user_type"] = user.user_type

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

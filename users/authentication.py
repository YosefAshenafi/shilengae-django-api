from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions

from users.models import BlacklistedToken

class JsonWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        is_blacklisted = BlacklistedToken.is_blacklisted(self.get_jwt_value(request))
        if is_blacklisted:
            raise exceptions.AuthenticationFailed('Token is not valid anymore')
        return super().authenticate(request)
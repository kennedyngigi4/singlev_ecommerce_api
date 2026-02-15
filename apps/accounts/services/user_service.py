
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

class UserService:


    @staticmethod
    def login_user(email, password):
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        
        refresh = RefreshToken.for_user(user)

        response = {
            "success": True,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": str(user.id),
            "email": user.email,
            "fullname": user.fullname,
            "role": user.role,
        }

        return response




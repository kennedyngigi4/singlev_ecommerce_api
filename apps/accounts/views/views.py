from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from django.conf import settings

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models.models import User
from apps.accounts.serializers.serializers import RegisterSerializer, LoginSerializer, UserReadSerializer, PasswordResetConfirmationSerializer, PasswordResetRequestSerializer
from apps.accounts.services.user_service import UserService


token_generator = PasswordResetTokenGenerator()

# Create your views here.


class RegisterView(APIView):
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True,  "message": "Registration successful."})
        
        return Response({ "success": False, "message": "An error occured.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





class LoginView(APIView):

    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            result = UserService.login_user(
                serializer.validated_data["email"],
                serializer.validated_data["password"]
            )

            return Response(result, status=status.HTTP_200_OK)




class UserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user

        profile = User.objects.prefetch_related("profile", "locations").filter(id=user.id).first()
        serializer = UserReadSerializer(profile)

        return Response(serializer.data)






class PasswordResetRequestView(APIView):

    def post(self, request):

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            reset_link = f"https://quza.co.ke/reset-password?uid={uid}&token={token}"

            send_mail(
                "Reset your password",
                f"Click the link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
            )

        except User.DoesNotExist:
            pass

        return Response(
            {"message": "If the email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )



class PasswordResetConfirmView(APIView):

    def post(self, request):

        serializer = PasswordResetConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response(
                {"error": "Invalid reset link"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not token_generator.check_token(user, token):
            return Response(
                {"error": "Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK
        )





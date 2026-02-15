from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models.models import User
from apps.accounts.serializers.serializers import RegisterSerializer, LoginSerializer, UserReadSerializer
from apps.accounts.services.user_service import UserService

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






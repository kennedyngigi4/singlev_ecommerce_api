from rest_framework import serializers

from apps.accounts.models.models import *
from apps.accounts.models.customer_profile import *


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
           "fullname", "email", "phone", "role", "password"
        ]
        extra_kwargs = { "password": { "write_only": True }}

    def create(self, validated_data):
        user  = User.objects.create_user(
            fullname=validated_data["fullname"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            role=validated_data["role"],
            password=validated_data["password"],
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)




class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            "gender", "dob", "profile_image"
        ]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLocation
        fields = [
            "address", "lat", "lng"
        ]

class UserReadSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
           "fullname", "email", "phone", "role", "date_joined", "locations", "profile"
        ]



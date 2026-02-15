from rest_framework import serializers
from apps.accounts.models.models import *

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "fullname", "email", "role", "phone"
        ]
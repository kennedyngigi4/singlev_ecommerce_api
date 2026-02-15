import uuid
from django.db import models

from .models import User


class CustomerProfile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    gender = models.CharField(max_length=8, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="profiles", null=True, blank=True)


    def __str__(self):
        return f"{self.user.fullname}"


class CustomerLocation(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="locations")

    address = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=12, decimal_places=8)
    lng = models.DecimalField(max_digits=12, decimal_places=8)

    region = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)


    is_default = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.fullname} - {self.address}"


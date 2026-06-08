import uuid
from django.db import models
from apps.accounts.models.models import User

class VendorProfile(models.Model):

    OPERATIONAL_STATUS = [
        ( "pending", "pending"),
        ( "approved", "approved"),
        ( "denied", "denied"),
        ( "suspended", "suspended"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_profile")

    business_name = models.CharField(max_length=255, unique=True)
    business_phone = models.CharField(max_length=25)
    business_location = models.CharField(max_length=255)
    business_latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    business_longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)

    business_status = models.CharField(max_length=100, choices=OPERATIONAL_STATUS, default="pending")

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="vendor_creator", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.business_name} by {self.user.email}"


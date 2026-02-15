import uuid
from django.db import models
from apps.orders.models import *
# Create your models here.


class MpesaPayment(models.Model):

    STATUS_CHOICES = [
        ( "pending", "pending" ),
        ( "paid", "paid" ),
        ( "failed", "failed" ),
    ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name="payments")
    checkout_request_id = models.CharField(max_length=100, null=True)
    transaction_code = models.CharField(max_length=30, unique=True, null=True, blank=True)

    result_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    result_desc = models.CharField(max_length=100, unique=True, null=True, blank=True)


    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    raw_payload = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.transaction_code} - {self.status}"

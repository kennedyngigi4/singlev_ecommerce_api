import uuid
import random
import string

from django.db import models, transaction
from django.db.models import Max

from apps.accounts.models.models import User
from apps.products.models.models import Product, ProductVariant
# Create your models here.



def genOrderId(order_number: int) -> str:
    random_part = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=7)
    )
    return f"OR{order_number}{random_part}"


class Order(models.Model):

    PAYMENT_STATUS = [
        ( "pending", "pending" ),
        ( "paid", "paid" ),
        ( "failed", "failed" ),
    ]

    STATUS = [
        ( "pending", "pending" ),
        ( "delivered", "delivered" ),
        ( "in_transit", "in_transit" ),
        ( "cancelled", "cancelled" ),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    order_number = models.PositiveBigIntegerField(null=True, blank=True, unique=True)
    order_id = models.CharField(max_length=60, unique=True, editable=False)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    served_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="seller")

    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default="pending")
    status = models.CharField(max_length=50, choices=STATUS, default="pending")

    mpesa_number = models.CharField(max_length=20, null=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)

    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mpesa_receipt = models.CharField(max_length=100, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.order_number:
            with transaction.atomic():
                last_number = (
                    Order.objects.select_for_update()
                    .aggregate(max_no=Max("order_number"))
                    .get("max_no") or 0
                )

                self.order_number = last_number + 1
                self.order_id = genOrderId(self.order_number)

        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.order_id)
    



class OrderItem(models.Model):
    STATUS = [
        ( "pending", "pending" ),
        ( "in_transit", "in_transit" ),
        ( "delivered", "delivered" ),
        ( "cancelled", "cancelled" ),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    order = models.ForeignKey(Order, on_delete=models.Case, null=True, related_name="order_items")
    product = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS, default="pending")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.product.product.name} {self.product.price} - {self.order.order_id}"


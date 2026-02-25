import re
from django.core.exceptions import ValidationError
from rest_framework.validators import ValidationError
from apps._helpers.payments.mpesa import MpesaService


class OrderService:

    @staticmethod
    def normalize_phone_number(phone_number: str) -> str:
        if not phone_number:
            raise ValidationError("MPesa number is required")

        number = str(phone_number).strip()

        number = number.replace(" ", "")
        if number.startswith("+"):
            number = number[1:]

        
        if number.startswith("07"):
            number = "254" + number[1:]

        elif number.startswith("01"):
            number = "254" + number[1:]

        elif number.startswith("254"):
            pass

        else:
            raise ValidationError(
                "Invalid phone format. Must start with 07, 01, +254 or 254"
            )

        pattern = r"^254\d{9}$"
        if not re.match(pattern, number):
            raise ValidationError("Phone number must be in format 254XXXXXXXXX")

        return number
    

    @staticmethod
    def mpesa_order(order):

        if not order:
            raise ValidationError("Order is required")
        
        phone_number = OrderService.normalize_phone_number(order.mpesa_number)

        mpesa = MpesaService()
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=int(round(order.total_amount)),
            reference=f"{order.order_id}"
        )

        order.checkout_request_id = response["CheckoutRequestID"]
        order.merchant_request_id = response["MerchantRequestID"]
        order.save(update_fields=["checkout_request_id", "merchant_request_id"])

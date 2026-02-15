from rest_framework.validators import ValidationError
from apps._helpers.payments.mpesa import MpesaService


class OrderService:

    @staticmethod
    def mpesa_order(order):

        if not order:
            raise ValidationError("Order is required")

        mpesa = MpesaService()
        response = mpesa.stk_push(
            phone_number=order.mpesa_number,
            amount=int(round(order.total_amount)),
            reference=f"{order.order_id}"
        )

        order.checkout_request_id = response["CheckoutRequestID"]
        order.merchant_request_id = response["MerchantRequestID"]
        order.save(update_fields=["checkout_request_id", "merchant_request_id"])

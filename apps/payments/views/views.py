import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order
from apps.payments.models import MpesaPayment


@csrf_exempt
@require_POST
def callbackView(request):
    data = json.loads(request.body.decode("utf-8"))
    print("MPESA CALLBACK >>>", data)

    callback = data.get("Body", {}).get("stkCallback", {})
    checkout_id = callback.get("CheckoutRequestID")

    if not checkout_id:
        return JsonResponse({
            "ResultCode": 1,
            "ResultDesc": "CheckoutRequestID missing"
        })

    order = Order.objects.filter(checkout_request_id=checkout_id).first()

    if not order:
        return JsonResponse({
            "ResultCode": 1,
            "ResultDesc": "Order not found"
        })

    result_code = callback.get("ResultCode")
    result_desc = callback.get("ResultDesc")

    # ✅ SUCCESS
    if result_code == 0:
        metadata = callback.get("CallbackMetadata", {}).get("Item", [])

        def get_value(name):
            return next((i["Value"] for i in metadata if i["Name"] == name), None)

        mpesa_receipt = get_value("MpesaReceiptNumber")
        amount = get_value("Amount")
        phone_number = get_value("PhoneNumber")

        MpesaPayment.objects.create(
            order=order,
            checkout_request_id=checkout_id,
            transaction_code=mpesa_receipt,
            amount=amount,
            phone_number=phone_number,
            status="paid",
            result_code=result_code,
            result_desc=result_desc,
            raw_payload=data,
        )

        order.payment_status = "paid"
        order.mpesa_receipt = mpesa_receipt
        order.paid_amount = amount
        order.save(update_fields=["payment_status", "mpesa_receipt", "paid_amount"])

    # ❌ FAILED / CANCELLED
    else:
        MpesaPayment.objects.create(
            order=order,
            checkout_request_id=checkout_id,
            amount=order.total_amount,
            phone_number=order.mpesa_number,
            status="failed",
            result_code=result_code,
            result_desc=result_desc,
            raw_payload=data,
        )

        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])

    # M-Pesa expects THIS exact response
    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })
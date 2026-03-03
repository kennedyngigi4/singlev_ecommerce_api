import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.orders.models import Order
from apps.payments.models import MpesaPayment


import logging
logger = logging.getLogger("mpesa")

@csrf_exempt
@require_POST
def callbackView(request):
    data = json.loads(request.body.decode("utf-8"))
    logger.error(f"MPESA CALLBACK DATA: {data}")

    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })



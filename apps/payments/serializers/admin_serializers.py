from rest_framework import serializers

from apps.payments.models import *

class MpesaPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = [
            "id", "order", "transaction_code", "phone_number", "amount", "status", "created_at"
        ]



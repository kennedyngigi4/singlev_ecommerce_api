import base64
import requests
from django.conf import settings
from datetime import datetime

from apps.app_config.models import MpesaConfig




class MpesaService:

    def __init__(self):
        self.config = MpesaConfig.objects.filter(is_active=True).first()

        if not self.config:
            return
        
        self.base_url = (
            "https://sandbox.safaricom.co.ke"
            if self.config.environment == "sandbox"
            else "https://api.safaricom.co.ke"
        )
        


    def access_token(self):

        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.config.consumer_key, self.config.consumer_secret))
        response.raise_for_status()
        return response.json()["access_token"]
    

    def mpesa_password(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data = f"{self.config.shortcode}{self.config.passkey}{timestamp}"
        password = base64.b64encode(data.encode()).decode()
        return password, timestamp
    

    def stk_push(self, phone_number, amount, reference="ORDER"):
        access_token = self.access_token()
        password, timestamp = self.mpesa_password()
        shortcode = self.config.shortcode

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://636b-154-123-152-163.ngrok-free.app/v1/payments/callback/",
            "AccountReference": reference,
            "TransactionDesc": "Payment"
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)

        # 🔥 IMPORTANT FOR DEBUGGING
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print(response)

        response.raise_for_status()

        data = response.json()

        return data






    
    

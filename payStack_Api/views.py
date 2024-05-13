from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.conf import settings
from .serializers import PaymentSerializer

from decimal import Decimal

class PaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            amount = float(serializer.validated_data["amount"])
            # Process payment using Paystack API
            paystack_secret_key = settings.PAYSTACK_SECRET_KEY
            paystack_api_url = "https://api.paystack.co/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "email": serializer.validated_data["email"],
                "amount": amount * 100,  # Amount in kobo
                "reference": serializer.validated_data["reference"],
                "plan": serializer.validated_data.get("plan"),
            }
            response = requests.post(paystack_api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

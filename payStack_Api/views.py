from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import uuid
from django.conf import settings
from .serializers import (
    PaymentSerializer,
    DirectChargeSerializer,
    DirectChargeRequestSerializer,
    DirectChargeResponseSerializer,
    DirectChargeOTPSerializer,
    DirectChargeOTPResponseSerializer,
)
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from decimal import Decimal

class PaymentView(APIView):
    @extend_schema(
        request=PaymentSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        description="Initialize a Paystack transaction using the standard checkout flow.",
    )
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
                "amount": int(amount * 100),
                "reference": serializer.validated_data["reference"],
                "plan": serializer.validated_data.get("plan"),
            }
            response = requests.post(paystack_api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectChargeView(APIView):
    @extend_schema(
        request=DirectChargeRequestSerializer,
        responses={200: DirectChargeResponseSerializer, 400: OpenApiTypes.OBJECT},
        description="Create a direct Paystack charge and optionally return an OTP requirement.",
    )
    def post(self, request):
        serializer = DirectChargeRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            paystack_secret_key = settings.PAYSTACK_SECRET_KEY
            headers = {
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json",
            }

            amount = int(data["amount"] * Decimal(100))
            reference = data.get("reference") or f"order-{uuid.uuid4().hex[:12]}"

            method = data.get('method', 'mobile_money')

            # Mobile money/direct charge via /charge
            if method == 'mobile_money':
                paystack_api_url = "https://api.paystack.co/charge"
                payload = {
                    "amount": amount,
                    "reference": reference,
                    "currency": data.get("currency", settings.PAYSTACK_CURRENCY),
                    "mobile_money": {
                        "phone": data["phone"],
                        "provider": data.get("provider"),
                    }
                }
                if data.get("email"):
                    payload["email"] = data["email"]
                response = requests.post(paystack_api_url, json=payload, headers=headers)

            # Card charge expects an authorization_code (tokenized card)
            elif method == 'card':
                if not data.get('authorization_code'):
                    return Response({"detail": "authorization_code required for card charges."}, status=400)
                paystack_api_url = "https://api.paystack.co/charge"
                payload = {
                    "amount": amount,
                    "reference": reference,
                    "currency": data.get("currency", settings.PAYSTACK_CURRENCY),
                    "authorization_code": data.get('authorization_code'),
                }
                if data.get("email"):
                    payload["email"] = data["email"]
                response = requests.post(paystack_api_url, json=payload, headers=headers)

            # Bank transfer: use transaction initialize with channels set to bank
            elif method == 'bank':
                paystack_api_url = "https://api.paystack.co/transaction/initialize"
                payload = {
                    "amount": amount,
                    "reference": reference,
                    "currency": data.get("currency", settings.PAYSTACK_CURRENCY),
                    "channels": ["bank"],
                }
                if data.get("email"):
                    payload["email"] = data["email"]
                # pass bank details as metadata (optional)
                metadata = {}
                if data.get('bank_account_number'):
                    metadata['bank_account_number'] = data.get('bank_account_number')
                if data.get('bank_code'):
                    metadata['bank_code'] = data.get('bank_code')
                if metadata:
                    payload['metadata'] = metadata
                response = requests.post(paystack_api_url, json=payload, headers=headers)

            else:
                return Response({"detail": "Unsupported payment method."}, status=400)

            paystack_response = response.json()
            success = paystack_response.get("status") is True
            # Build standardized result
            result = {
                "status": success,
                "message": paystack_response.get("message", "Charge attempted"),
                "reference": reference,
                "data": paystack_response.get("data"),
            }

            if success and isinstance(paystack_response.get("data"), dict):
                if paystack_response["data"].get("status") == "send_otp":
                    result["next_step"] = "submit_otp"
                    result["display_text"] = paystack_response["data"].get(
                        "display_text", "Please complete the OTP sent to the customer."
                    )
            return Response(result, status=response.status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectChargeOTPView(APIView):
    @extend_schema(
        request=DirectChargeOTPSerializer,
        responses={200: DirectChargeOTPResponseSerializer, 400: OpenApiTypes.OBJECT},
        description="Submit the OTP for a pending Paystack direct charge.",
    )
    def post(self, request):
        serializer = DirectChargeOTPSerializer(data=request.data)
        if serializer.is_valid():
            paystack_secret_key = settings.PAYSTACK_SECRET_KEY
            paystack_api_url = "https://api.paystack.co/charge/submit_otp"
            headers = {
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json",
            }
            data = serializer.validated_data
            payload = {
                "reference": data["reference"],
                "otp": data["otp"],
            }
            response = requests.post(paystack_api_url, json=payload, headers=headers)
            paystack_response = response.json()
            success = paystack_response.get("status") is True
            result = {
                "status": success,
                "message": paystack_response.get("message", "OTP submission attempted"),
                "reference": data["reference"],
                "data": paystack_response.get("data"),
            }
            return Response(result, status=response.status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

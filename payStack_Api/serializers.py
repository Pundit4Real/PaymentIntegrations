from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=100)
    plan = serializers.CharField(max_length=100, required=False)


class DirectChargeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20)
    provider = serializers.CharField(max_length=20, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=3, required=False, default='GHS')
    authorization_code = serializers.CharField(max_length=255, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, data):
        if data.get('phone') and not data.get('provider'):
            raise serializers.ValidationError({
                'provider': 'Provider is required when using mobile money.'
            })
        return data


class DirectChargeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    # payment method: 'mobile_money', 'card', or 'bank'
    method = serializers.ChoiceField(choices=['mobile_money', 'card', 'bank'], required=False, default='mobile_money')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    provider = serializers.CharField(max_length=20, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=3, required=False, default='GHS')

    # bank-specific fields (optional)
    bank_account_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    bank_code = serializers.CharField(max_length=30, required=False, allow_blank=True)

    # card-specific (we expect an authorization_code when charging a card)
    authorization_code = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, data):
        method = data.get('method', 'mobile_money')
        if method == 'mobile_money':
            if not data.get('phone') or not data.get('provider'):
                raise serializers.ValidationError({
                    'phone': 'Phone and provider are required for mobile money.'
                })
        if method == 'card':
            if not data.get('authorization_code'):
                raise serializers.ValidationError({
                    'authorization_code': 'authorization_code is required for card charges.'
                })
        if method == 'bank':
            # bank flow will use transaction initialize; bank details optional
            pass
        return data


class DirectChargeResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    reference = serializers.CharField()
    data = serializers.JSONField(required=False)
    next_step = serializers.CharField(required=False)
    display_text = serializers.CharField(required=False)


class DirectChargeOTPSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    otp = serializers.CharField(max_length=12)


class DirectChargeOTPResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    reference = serializers.CharField()
    data = serializers.JSONField(required=False)

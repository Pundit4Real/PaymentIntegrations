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
    phone = serializers.CharField(max_length=20)
    provider = serializers.CharField(max_length=20, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=3, required=False, default='GHS')

    def validate(self, data):
        if data.get('phone') and not data.get('provider'):
            raise serializers.ValidationError({
                'provider': 'Provider is required when using mobile money.'
            })
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

from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=100)
    plan = serializers.CharField(max_length=100, required=False)

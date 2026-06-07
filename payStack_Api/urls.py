from django.urls import path
from .views import PaymentView, DirectChargeView, DirectChargeOTPView

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
    path('direct-charge/', DirectChargeView.as_view(), name='direct-charge'),
    path('direct-charge/submit-otp/', DirectChargeOTPView.as_view(), name='direct-charge-submit-otp'),
]

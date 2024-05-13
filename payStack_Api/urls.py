from django.urls import path
from .views import PaymentView  # Correct the import statement

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
]

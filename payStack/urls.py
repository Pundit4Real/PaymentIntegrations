from django.urls import path
from payStack.views import *

urlpatterns = [
    path('', initiate_payment, name='initiate-payment'),
    path('<str:ref>/', verify_payment, name='verify-payment'),
]

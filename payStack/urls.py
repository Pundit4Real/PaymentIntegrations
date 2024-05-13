from django.urls import path
from payStack.views import *

urlpatterns = [
    path('',initiate_payment, name='intiate-payment'),
    path('<str:ref>/',verify_payment, name='verify-payment'),
]

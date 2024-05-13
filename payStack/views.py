from django.shortcuts import render,get_object_or_404,redirect
from django.conf import settings
from django.http import HttpRequest,HttpResponse
from django.contrib import messages
from payStack.forms import PaymentForm
from payStack.models import Payment

# Create your views here.

def initiate_payment(request) -> str:
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save()
            return render(request,'make_payment.html',{'payment':payment,'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY})
    else:
        payment_form = PaymentForm() 
    return render(request,'initiate_payment.html', {'payment_form':payment_form,})


def verify_payment(request, ref) ->str:
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, "Verification Successfull")
    else:
        messages.error(request, "verification failed, Try again")
    return redirect('intiate-payment')
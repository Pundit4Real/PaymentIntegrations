from django.db import models
import secrets
from payStack.paystack import PayStack
# Create your models here.

class Payment(models.Model):
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200,default='')
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Payment'
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f"Payment: {self.amount}"
    
    def save(self,*args,**kwargs) -> None:
        while not self.ref:
            ref =secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> str:
        return self.amount * 100
    
    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if isinstance(result, dict) and 'amount' in result:
                if result['amount'] / 100 == self.amount:
                    self.verified = True
                self.save()
        if self.verified:
            return True
        return False

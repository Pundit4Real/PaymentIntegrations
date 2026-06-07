from django.conf import settings
import requests

class PayStack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    base_url = 'https://api.paystack.co'

    def verify_payment(self, ref, *args, **kwargs):
        path = f'/transactions/verify/{ref}'

        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
            "Content-Type": 'application/json',
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            status = response_data.get('status')
            if status == True:
                return 'success', response_data.get('data')
            else:
                return 'failure', response_data.get('message')
        else:
            return 'error', f"HTTP Error: {response.status_code}"



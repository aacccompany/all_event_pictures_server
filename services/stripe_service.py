import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(cart_items, success_url, cancel_url):
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'thb', # You might want to make this configurable
                'product_data': {
                    'name': item.image.public_id.split('/')[-1],
                    'images': [item.image.secure_url],
                },
                'unit_amount': 2000, # Example: $20.00 per image
            },
            'quantity': 1,
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card', 'promptpay'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return checkout_session.url

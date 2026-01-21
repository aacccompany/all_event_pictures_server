import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(cart_items, success_url, cancel_url):
    line_items = []
    for item in cart_items:
        # Determine per-image price from the event. Fallback to 2000 satang (THB 20).
        event = getattr(item.image, 'event', None)
        unit_amount = 2000
        if event and getattr(event, 'image_price', None):
            try:
                unit_amount = int(event.image_price)
            except Exception:
                unit_amount = 2000
        line_items.append({
            'price_data': {
                'currency': 'thb', # You might want to make this configurable
                'product_data': {
                    'name': item.image.public_id.split('/')[-1],
                    'images': [item.image.secure_url],
                },
                'unit_amount': unit_amount,
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

def retrieve_checkout_session(session_id):
    return stripe.checkout.Session.retrieve(session_id)

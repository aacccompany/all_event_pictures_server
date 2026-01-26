import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")



def create_checkout_session(cart_items, success_url, cancel_url):
    line_items = []
    total_amount = 0
    for item in cart_items:
        # Determine per-image price from the event. Fallback to 2000 satang (THB 20).
        event = getattr(item.image, 'event', None)
        unit_amount = 2000
        if event and getattr(event, 'image_price', None):
            try:
                unit_amount = int(event.image_price)
            except Exception:
                unit_amount = 2000
        
        total_amount += unit_amount
        line_items.append({
            'price_data': {
                'currency': 'thb', 
                'product_data': {
                    'name': item.image.public_id.split('/')[-1],
                    'images': [item.image.secure_url],
                },
                'unit_amount': unit_amount,
            },
            'quantity': 1,
        })
    
    # Minimum 10 THB (1000 Satang)
    if total_amount < 1000:
        raise Exception("Total purchase amount must be at least 10 THB.")

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

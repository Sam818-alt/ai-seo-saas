from flask import Blueprint, request, jsonify
import os, datetime
from models import SessionLocal, User, Subscription
# Payment SDKs - optional import (installed via requirements)
try:
    import stripe
except Exception:
    stripe = None
try:
    import razorpay
except Exception:
    razorpay = None
try:
    import paypalrestsdk
except Exception:
    paypalrestsdk = None

payment_bp = Blueprint('payment', __name__)

PLANS = {
    "basic": {"name":"Basic", "price_usd":29, "blogs_per_month":50, "id":"basic"},
    "pro": {"name":"Pro", "price_usd":49, "blogs_per_month":200, "id":"pro"},
    "premium": {"name":"Premium", "price_usd":99, "blogs_per_month":9999999, "id":"premium"}
}

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
RAZORPAY_KEY = os.getenv('RAZORPAY_KEY')
RAZORPAY_SECRET = os.getenv('RAZORPAY_SECRET')

if STRIPE_API_KEY and stripe:
    stripe.api_key = STRIPE_API_KEY

if PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET and paypalrestsdk:
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET
    })

if RAZORPAY_KEY and RAZORPAY_SECRET and razorpay:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
else:
    razorpay_client = None

@payment_bp.route('/plans', methods=['GET'])
def get_plans():
    return jsonify({"plans": PLANS})

@payment_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    data = request.json or {}
    user_id = data.get('user_id')
    plan_id = data.get('plan_id')
    provider = data.get('provider', 'stripe')
    if plan_id not in PLANS:
        return jsonify({"error":"invalid_plan"}), 400
    plan = PLANS[plan_id]

    if provider == 'stripe':
        if not (STRIPE_API_KEY and stripe):
            return jsonify({"error":"stripe_not_configured"}), 500
        try:
            amount = int(plan['price_usd'] * 100)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': f"{plan['name']} Plan"},
                        'unit_amount': amount,
                        'recurring': {'interval': 'month'}
                    },
                    'quantity': 1
                }],
                metadata={'user_id': user_id or 'guest', 'plan_id': plan_id},
                success_url=os.getenv('SUCCESS_URL', 'http://localhost:3000') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=os.getenv('CANCEL_URL', 'http://localhost:3000')
            )
            return jsonify({"url": session.url, "session_id": session.id})
        except Exception as e:
            return jsonify({"error":"stripe_error", "details": str(e)}), 500

    elif provider == 'paypal':
        if not (PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET and paypalrestsdk):
            return jsonify({"error":"paypal_not_configured"}), 500
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": os.getenv('SUCCESS_URL', 'http://localhost:3000'),
                "cancel_url": os.getenv('CANCEL_URL', 'http://localhost:3000')
            },
            "transactions": [{
                "item_list": {"items": [{"name": f"{plan['name']} Plan", "sku": plan_id, "price": str(plan['price_usd']), "currency": "USD", "quantity": 1}]},
                "amount": {"total": str(plan['price_usd']), "currency": "USD"},
                "description": f"Subscription {plan_id}"
            }]
        })
        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval = str(link.href)
                    return jsonify({"url": approval, "order_id": payment.id})
            return jsonify({"error":"no_approval_url"}), 500
        else:
            return jsonify({"error":"paypal_create_failed", "details": payment.error}), 500

    elif provider == 'razorpay':
        if not razorpay_client:
            return jsonify({"error":"razorpay_not_configured"}), 500
        amount_inr = int(plan['price_usd'] * 82 * 100)
        order = razorpay_client.order.create({'amount': amount_inr, 'currency': 'INR', 'receipt': f'{user_id}_{plan_id}'})
        return jsonify({"order": order, "key": RAZORPAY_KEY})
    else:
        return jsonify({"error":"unsupported_provider"}), 400

@payment_bp.route('/webhook/stripe', methods=['POST'])
def webhook_stripe():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', None)
    if not STRIPE_WEBHOOK_SECRET or not stripe:
        return jsonify({'error':'webhook_not_configured'}), 400
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({'error':'invalid_signature', 'details': str(e)}), 400
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        plan_id = metadata.get('plan_id')
        db = SessionLocal()
        sub = Subscription(user_id=user_id, provider='stripe', provider_subscription_id=session.get('id'), plan=plan_id, status='active')
        db.add(sub)
        user = db.query(User).filter(User.id==user_id).first()
        if user:
            plan = PLANS.get(plan_id)
            if plan:
                user.plan = plan_id
                user.blogs_left = plan['blogs_per_month']
                db.add(user)
        db.commit(); db.close()
    return jsonify({'received': True})

@payment_bp.route('/webhook/paypal', methods=['POST'])
def webhook_paypal():
    return jsonify({'received': True})

@payment_bp.route('/webhook/razorpay', methods=['POST'])
def webhook_razorpay():
    return jsonify({'received': True})

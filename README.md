AI SEO SaaS Scaffold v6
-----------------------
Features:
- Multilingual blog generation (English base + optional auto-translate)
- Image generation (OpenAI Images or local stub) with S3 upload support
- Rich draft saving + images + selected image
- Secure auth (JWT) endpoints
- Payments integrated: Stripe, PayPal, Razorpay (checkout/session creation + webhook stubs)
- Dockerfiles & docker-compose (not included here) - use README from previous versions for Docker setup

Quick start (backend):
cd backend
python -m venv venv
source venv/bin/activate    # windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

Quick start (frontend):
cd frontend
npm install
npm start

Env vars for payments (if you want real integrations):
STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, RAZORPAY_KEY, RAZORPAY_SECRET

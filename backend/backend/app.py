from flask import Flask, jsonify
from flask_cors import CORS

# Blueprints
from auth import auth_bp
from blog_routes import blog_bp
from payment_routes import payment_bp

app = Flask(__name__)

# ✅ CORS setup - allow only React frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# ✅ Register Blueprints with API prefixes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(blog_bp, url_prefix='/api/blog')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

# ✅ Health Check
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'})

# ✅ Root for quick testing
@app.route('/')
def index():
    return "Flask backend is running. Try /api/ping"

if __name__ == '__main__':
    from models import init_db
    init_db()
    print("🔗 Flask is running. Routes:")
    print(app.url_map)
    app.run(host='0.0.0.0', port=5000, debug=True)

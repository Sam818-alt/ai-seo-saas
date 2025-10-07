from flask import Blueprint, request, jsonify
from models import SessionLocal, User
from passlib.hash import bcrypt
import jwt, os, datetime

auth_bp = Blueprint('auth', __name__)
SECRET = os.getenv('SECRET_KEY', 'change-me')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email'); password = data.get('password'); name = data.get('name','')
    if not email or not password:
        return jsonify({'error':'email_password_required'}), 400
    db = SessionLocal()
    if db.query(User).filter(User.email==email).first():
        db.close(); return jsonify({'error':'user_exists'}), 400
    hashed = bcrypt.hash(password)
    user = User(email=email, name=name, password_hash=hashed)
    db.add(user); db.commit(); db.refresh(user); db.close()
    token = create_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name}})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email'); password = data.get('password')
    if not email or not password:
        return jsonify({'error':'email_password_required'}), 400
    db = SessionLocal()
    user = db.query(User).filter(User.email==email).first()
    db.close()
    if not user or not bcrypt.verify(password, user.password_hash):
        return jsonify({'error':'invalid_credentials'}), 401
    token = create_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name}})

def create_token(user_id):
    payload = {'user_id': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}
    return jwt.encode(payload, SECRET, algorithm='HS256')

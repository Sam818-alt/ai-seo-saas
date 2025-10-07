from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os, uuid

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./dev.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(150))
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    plan = Column(String(50), default='free')
    blogs_left = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    keyword = Column(String(300))
    title = Column(String(500))
    meta_desc = Column(String(300))
    hashtags = Column(JSON)
    content_original = Column(Text)
    content_translated = Column(Text)
    language = Column(String(50), default='English')
    images = Column(JSON)
    selected_image = Column(String)
    status = Column(String, default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    provider = Column(String(50))  # stripe / paypal / razorpay
    provider_subscription_id = Column(String(200))
    plan = Column(String(50))  # basic/pro/premium
    status = Column(String(50)) # active/cancelled
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

from datetime import datetime
from backend.db import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    theme = db.Column(db.String(50), default="light")
    custom_domain = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    links = db.relationship('Link', backref='user', lazy=True)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    url = db.Column(db.String(500))
    position = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))
    ip_address = db.Column(db.String(50))
    country = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

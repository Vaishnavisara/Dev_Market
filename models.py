from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(10), nullable=False)  # 'client' or 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True, foreign_keys='Project.client_id')
    company_profile = db.relationship('Company', backref='user', lazy=True, uselist=False)
    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    payments = db.relationship('Payment', backref='user', lazy=True)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(120))
    services = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Projects this company is assigned to
    projects = db.relationship('Project', backref='company', lazy=True, foreign_keys='Project.company_id')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'completed'
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationship with payments
    payments = db.relationship('Payment', backref='project', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    # Optional project reference
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='messages')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    stripe_payment_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

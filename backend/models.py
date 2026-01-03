from backend.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='user', nullable=False)
    
    # Relationships
    resumes = db.relationship('Resume', backref='owner', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False) # Link to JD
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='Pending')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Job
    job = db.relationship('JobDescription', backref='resumes')

class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

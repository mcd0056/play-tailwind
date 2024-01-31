from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy ORM instance
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    conversations = db.relationship('ChatConversation', backref='user', lazy=True)
    openai_api_key = db.Column(db.String(200), nullable=True) 

# Define the ChatConversation model
class ChatConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    response = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Define the GeneratedImage model
class GeneratedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt = db.Column(db.String(500), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)  # To store image data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

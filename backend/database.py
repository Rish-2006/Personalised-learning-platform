# Flask-SQLAlchemy models for User and Lesson
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	lessons = db.relationship('Lesson', backref='user', lazy=True)

class Lesson(db.Model):
	__tablename__ = 'lessons'
	id = db.Column(db.Integer, primary_key=True)
	topic = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

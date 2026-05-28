# --- Step 1: Load environment variables ---
from dotenv import load_dotenv
import os
import re # Added for URL cleaning
load_dotenv()

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from database import db, User, Lesson
from flask_bcrypt import Bcrypt
from flask_cors import CORS
# --- Configuration ---
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

bcrypt = Bcrypt(app)
# --- Database Configuration (FIXED FOR RENDER) ---
database_url = os.getenv("DATABASE_URL")

# FIX: SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'
# We also add '+psycopg2' to be explicit about the driver
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    # Fallback to local SQLite if no DATABASE_URL is found
    database_url = "sqlite:///learning_platform.db"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

with app.app_context():
    db.create_all()

import urllib.request
import json

def generate_ai_content(prompt):
    url = 'https://text.pollinations.ai/'
    data = json.dumps({'messages': [{'role': 'user', 'content': prompt}], 'model': 'openai'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        return response.read().decode('utf-8')
    except Exception as e:
        print(f"AI Provider Error: {e}")
        return "An error occurred with the AI provider."

# --- API Routes ---

@app.route('/')
def home():
    return 'Learning Platform API is Live!'

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, email, and password required'}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': f'User {username} registered successfully!'}), 201
    except Exception as e:
        print(f"!!! REGISTER ERROR: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid username or password'}), 401
            
        return jsonify({'message': f'User {username} logged in successfully!'}), 200
    except Exception as e:
        print(f"!!! LOGIN ERROR: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        response_text = generate_ai_content(user_message)
        return jsonify({'reply': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_lesson', methods=['POST'])
def generate_lesson():
    try:
        data = request.get_json()
        topic = data.get('topic')
        username = data.get('username')
        if not topic:
            return jsonify({'error': 'Topic required'}), 400
        
        prompt = f"Generate a detailed, beginner-friendly lesson on the topic: {topic}. Use headings and bullet points."
        response_text = generate_ai_content(prompt)
        
        # Save progress automatically
        user = User.query.filter_by(username=username).first() if username else User.query.first()
        if user:
            lesson = Lesson(topic=topic, content=response_text, user_id=user.id)
            db.session.add(lesson)
            db.session.commit()

        return jsonify({'topic': topic, 'lesson_content': response_text})
    except Exception as e:
        print(f"LESSON ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/revision_notes', methods=['POST'])
def revision_notes():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text required'}), 400
        
        prompt = f"Create concise revision notes in bullet points for:\n\n{text}"
        response_text = generate_ai_content(prompt)
        return jsonify({'notes': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_assessment', methods=['POST'])
def generate_assessment():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text required'}), 400
            
        prompt = f"""Based on the following lesson, generate a JSON object for a multiple-choice assessment with exactly 3 questions.
Each question must have an array of 4 options and a field indicating the correct answer's text.
Format strictly as: {{"questions": [{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}]}}

Lesson content:
{text}"""
        response_text = generate_ai_content(prompt)
        
        # Clean JSON response
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
            
        return jsonify(cleaned_text.strip())
    except Exception as e:
        print(f"ASSESSMENT ERROR: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    lessons = Lesson.query.filter_by(user_id=user.id).all()
    progress_data = [{'topic': l.topic, 'content': l.content} for l in lessons]
    return jsonify({'progress': progress_data})

# --- Server Start ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

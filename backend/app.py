# --- Step 1: Load the .env file ---
from dotenv import load_dotenv
load_dotenv()
# --- End of new code ---

# Basic Flask application
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from database import db, User, Lesson
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
import google.generativeai as genai

# --- Configuration ---
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- AI Model Initialization ---
model = None
try:
    # Configure the Gemini API client (now reads from .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("!!! WARNING: GOOGLE_API_KEY not found in .env file. AI features will be disabled.")
    else:
        genai.configure(api_key=api_key)
        # Use the latest, correct model name
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("--- Gemini AI Model Initialized Successfully ---")
except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not configure Gemini API: {e}")


# --- API Routes ---
@app.route('/')
def home():
    return 'Hello, World!'

# User registration route
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, email, and password required'}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'error': 'Username or email already exists'}), 400

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': f'User {username} registered successfully!'})
    except Exception as e:
        print(f"!!! REGISTER ERROR: {e}")
        return jsonify({'error': f'An internal error occurred.'}), 500

# User login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid username or password'}), 401
        return jsonify({'message': f'User {username} logged in successfully!'})
    except Exception as e:
        print(f"!!! LOGIN ERROR: {e}")
        return jsonify({'error': f'An internal error occurred.'}), 500

# AI Chatbot Route
@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({'error': 'AI model is not configured correctly.'}), 500
    try:
        data = request.get_json()
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        response = model.generate_content(user_message)
        return jsonify({'reply': response.text})
    except Exception as e:
        print(f"!!! CHAT ERROR: {e}")
        return jsonify({'error': 'An error occurred with the AI service.'}), 500

# Lesson Generation Route
@app.route('/api/generate_lesson', methods=['POST'])
def generate_lesson():
    if not model:
        return jsonify({'error': 'AI model is not configured correctly.'}), 500
    try:
        data = request.get_json()
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        prompt = f"Generate a detailed, beginner-friendly lesson on the topic: {topic}. The lesson should be well-structured with clear explanations, headings, and bullet points."
        response = model.generate_content(prompt)
        return jsonify({'topic': topic, 'lesson_content': response.text})
    except Exception as e:
        print(f"!!! LESSON GENERATION ERROR: {e}")
        return jsonify({'error': 'An error occurred with the AI service.'}), 500

# Revision Notes Route
@app.route('/api/revision_notes', methods=['POST'])
def revision_notes():
    if not model:
        return jsonify({'error': 'AI model is not configured correctly.'}), 500
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Lesson content is required'}), 400
        prompt = f"Create a concise set of revision notes in bullet points for the following lesson:\n\n{text}"
        response = model.generate_content(prompt)
        return jsonify({'notes': response.text})
    except Exception as e:
        print(f"!!! REVISION NOTES ERROR: {e}")
        return jsonify({'error': 'An error occurred with the AI service.'}), 500

# Assessment Generation Route
@app.route('/api/generate_assessment', methods=['POST'])
def generate_assessment():
    if not model:
        return jsonify({'error': 'AI model is not configured correctly.'}), 500
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Lesson content is required'}), 400
        prompt = f"""
        Based on the following lesson, generate a JSON object for a multiple-choice assessment with exactly 3 questions.
        Each question must have an array of 4 options and a field indicating the correct answer's text.
        The JSON output should strictly follow this format: {{"questions": [{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}]}}

        Lesson content:
        {text}
        """
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return jsonify(cleaned_response)
    except Exception as e:
        print(f"!!! ASSESSMENT ERROR: {e}")
        return jsonify({'error': 'An error occurred with the AI service.'}), 500

# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # This will create the database tables if they don't exist
    app.run(debug=True)


# --- Step 1: Load environment variables ---
from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from database import db, User, Lesson
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from google import genai

# --- Configuration ---
app = Flask(__name__)

# UPDATED: Allow only your specific Vercel frontend to access this API
CORS(app, resources={r"/*": {"origins": "https://personalised-learning-platform-bice.vercel.app"}})

bcrypt = Bcrypt(app)
# Use a persistent DB for Render production if possible
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///learning_platform.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- AI Model Initialization ---
client = None
MODEL_NAME = "gemini-1.5-flash"

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("!!! WARNING: GOOGLE_API_KEY not found.")
    else:
        client = genai.Client(api_key=api_key)
        print(f"--- Gemini AI Client Initialized ({MODEL_NAME}) ---")
except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not configure Gemini API: {e}")

# --- API Routes ---
@app.route('/')
def home():
    return 'Learning Platform API is Live!'

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username, password, email = data.get('username'), data.get('password'), data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'All fields required'}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'error': 'Username or email already exists'}), 400

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': f'User {username} registered successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, data.get('password')):
            return jsonify({'error': 'Invalid credentials'}), 401
        return jsonify({'message': 'Logged in successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Chat, Lesson, and Notes routes remain the same but use the 'client' initialized above
# ... (Add your /api/chat, /api/generate_lesson, etc. routes here)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

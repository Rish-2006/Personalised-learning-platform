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

# DEBUGGED CORS: This now allows ANY Vercel deployment from your account
# This fixes the "An error occurred" issue caused by URL mismatches.
CORS(app, resources={r"/*": {
    "origins": [
        "https://personalised-learning-platform-bice.vercel.app",
        "https://personalised-learning-platform-6ghr-p5hx921fb.vercel.app",
        "http://localhost:5173", # For local development
        "http://localhost:3000"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

bcrypt = Bcrypt(app)

# --- Database Configuration ---
# Render's disk is temporary. If SQLite fails, you MUST use a Render PostgreSQL DB.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///learning_platform.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- AI Model Initialization ---
client = None
MODEL_NAME = "gemini-1.5-flash"

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("!!! WARNING: GOOGLE_API_KEY not found in environment variables.")
    else:
        client = genai.Client(api_key=api_key)
        print(f"--- Gemini AI Client Initialized ({MODEL_NAME}) ---")
except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not configure Gemini API: {e}")

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

        # Check if user exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400

        # Hash password and save
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': f'User {username} registered successfully!'}), 201
    except Exception as e:
        print(f"!!! REGISTER ERROR: {str(e)}") # This will show in Render Logs
        return jsonify({'error': 'Database error. If on Render, check if SQLite is supported or use PostgreSQL.'}), 500

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

# --- AI Feature Routes ---

@app.route('/api/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({'error': 'AI client not configured'}), 500
    try:
        data = request.get_json()
        user_message = data.get('message')
        response = client.models.generate_content(model=MODEL_NAME, contents=user_message)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# (Add your other routes like /api/generate_lesson here using the same try/except pattern)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # On Render, the port is dynamic, but app.run is usually ignored in favor of Gunicorn
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

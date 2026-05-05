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
from google import genai

# --- Configuration ---
app = Flask(__name__)

# CORS: Allows specified Vercel and local URLs
CORS(app, resources={r"/*": {
    "origins": [
        "https://personalised-learning-platform-bice.vercel.app",
        "https://personalised-learning-platform-6ghr-p5hx921fb.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

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

# --- AI Model Initialization ---
client = None
MODEL_NAME = "gemini-1.5-flash"

def init_ai():
    global client
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
            print(f"--- Gemini AI Client Initialized ({MODEL_NAME}) ---")
        else:
            print("!!! WARNING: GOOGLE_API_KEY not found.")
    except Exception as e:
        print(f"!!! CRITICAL ERROR: Could not configure Gemini API: {e}")

init_ai()

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
    if not client:
        return jsonify({'error': 'AI client not configured'}), 500
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        response = client.models.generate_content(model=MODEL_NAME, contents=user_message)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Server Start ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

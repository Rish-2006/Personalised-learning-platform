# Basic Flask application
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from database import db, User, Lesson
from flask_bcrypt import Bcrypt

from flask_cors import CORS
from ai_crew import learning_crew
from ai_graph import graph, LessonState



app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

bcrypt = Bcrypt(app)

    # Configure the database URI (update as needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with app
db.init_app(app)

from flask import request

@app.route('/')
def home():
	return 'Hello, World!'

@app.route('/api/data')
def api_data():
	return jsonify({'message': 'This is your data!'})


# User registration route
@app.route('/register', methods=['POST'])
def register():
	username = request.form.get('username')
	password = request.form.get('password')
	email = request.form.get('email')
	if not username or not password or not email:
		return jsonify({'error': 'Username, email, and password required'}), 400
	if User.query.filter((User.username == username) | (User.email == email)).first():
		return jsonify({'error': 'Username or email already exists'}), 400
	pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
	user = User(username=username, email=email, password_hash=pw_hash)
	db.session.add(user)
	db.session.commit()
	return jsonify({'message': f'User {username} registered successfully!'})


# User login route
@app.route('/login', methods=['POST'])
def login():
	username = request.form.get('username')
	password = request.form.get('password')
	if not username or not password:
		return jsonify({'error': 'Username and password required'}), 400
	user = User.query.filter_by(username=username).first()
	if not user or not bcrypt.check_password_hash(user.password_hash, password):
		return jsonify({'error': 'Invalid username or password'}), 401
	return jsonify({'message': f'User {username} logged in successfully!'})


# Endpoint to generate a lesson plan using Crew.ai and LangGraph
@app.route('/api/generate_lesson', methods=['POST'])
def generate_lesson():
	data = request.get_json()
	topic = data.get('topic')
	if not topic:
		return jsonify({'error': 'Topic is required'}), 400
	# Use Crew.ai to gather info and design curriculum (simulate for now)
	# researcher and curriculum_designer are part of learning_crew
	# For demonstration, just use LangGraph to simulate lesson flow
	state = LessonState(user_query=topic)
	graph.run(state)
	return jsonify({
		'topic': state.user_query,
		'lesson_content': state.lesson_content,
		'quiz_score': state.quiz_score
	})

if __name__ == '__main__':
	app.run(debug=True)

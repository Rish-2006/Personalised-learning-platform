# Personalized Learning Platform

An AI-powered web application designed to deliver customized learning experiences. This platform uses a crew of AI agents and a stateful graph to generate, adapt, and present educational content tailored to user needs.

## ✨ Key Features

-   *🤖 AI-Powered Lesson Generation*: Leverages CrewAI and LangGraph to dynamically create lesson plans on any given topic.
-   *🔐 User Authentication*: Secure user registration and login system using password hashing.
-   *🧠 Adaptive Learning Path*: A simulated adaptive learning loop that can regenerate content based on quiz performance, managed by a LangGraph state machine.
-   *⚙ Modular Backend*: Built with Flask, featuring a clean separation of concerns for the API, database models, and AI logic.
-   *🖥 Simple Frontend*: A clean and straightforward user interface built with HTML, CSS, and vanilla JavaScript.

## 🏛 Architecture Overview

The application is built around a central Flask backend that serves both the frontend pages and a JSON API.

1.  **Flask Application (app.py): The core of the backend. It handles HTTP requests, manages user authentication (/register, /login), and exposes the AI functionality through the /api/generate_lesson endpoint.
2.  **Database (database.py): Defines the data models for User and Lesson using Flask-SQLAlchemy, with SQLite as the database engine.
3.  **AI Crew (ai_crew.py): Sets up a multi-agent system using CrewAI. It defines a Researcher agent to gather information and a Curriculum Designer agent to structure it into a lesson. (Note: The current implementation simulates this and directly uses LangGraph).
4.  **AI Graph (ai_graph.py): Implements a state machine using LangGraph to manage the lifecycle of a lesson. It moves from generating content to analyzing feedback (a quiz score) and decides whether to regenerate the content or complete the lesson.
5.  **Frontend (.html files): Static HTML files provide the user interface for the landing page, registration, login, and a user dashboard. JavaScript is used on the registration page to handle form submission asynchronously.

## 🚀 Getting Started

Follow these instructions to get a local copy of the project up and running.

### Prerequisites

-   Python 3.8+
-   pip package manager
-   An OpenAI API Key

### Installation & Setup

1.  *Clone the repository:*
    bash
    git clone [https://github.com/your-username/personalized-learning-platform.git](https://github.com/your-username/personalized-learning-platform.git)
    cd personalized-learning-platform
    

2.  *Create and activate a virtual environment:*
    * *macOS/Linux:*
        bash
        python3 -m venv venv
        source venv/bin/activate
        
    * *Windows:*
        bash
        python -m venv venv
        .\venv\Scripts\activate
        

3.  *Install the required dependencies:*
    bash
    pip install Flask Flask-SQLAlchemy Flask-Bcrypt Flask-Cors crewai langgraph openai python-dotenv
    

4.  *Set up environment variables:*
    Create a file named .env in the root directory of the project and add your OpenAI API key:
    
    OPENAI_API_KEY='your-openai-api-key-here'
    
    The application uses python-dotenv to load this key automatically.

5.  *Initialize the database:*
    Open a Python shell in your terminal and run the following commands to create the learning_platform.db file and the necessary tables.
    python
    from app import app, db
    with app.app_context():
        db.create_all()
    

6.  *Run the Flask application:*
    bash
    python app.py
    
    The application will be available at http://127.0.0.1:5000.

##  API Endpoints

The application exposes the following API endpoints:

#### POST /register

Registers a new user.

-   *Content-Type*: application/x-www-form-urlencoded or application/json
-   *Body*:
    json
    {
        "username": "newuser",
        "email": "user@example.com",
        "password": "strongpassword123"
    }
    
-   *Success Response*: {'message': 'User newuser registered successfully!'}
-   *Error Response*: {'error': 'Username or email already exists'}

#### POST /login

Logs in an existing user.

-   *Content-Type*: application/x-www-form-urlencoded
-   *Body*:
    json
    {
        "username": "newuser",
        "password": "strongpassword123"
    }
    
-   *Success Response*: {'message': 'User newuser logged in successfully!'}
-   *Error Response*: {'error': 'Invalid username or password'}

#### POST /api/generate_lesson

Generates a lesson plan for a given topic using the AI graph.

-   *Content-Type*: application/json
-   *Body*:
    json
    {
        "topic": "Introduction to Quantum Mechanics"
    }
    
-   *Success Response*:
    json
    {
        "topic": "Introduction to Quantum Mechanics",
        "lesson_content": "Lesson on: Explain photosynthesis",
        "quiz_score": 0.85
    }
    
    *Note: The lesson_content currently uses a hardcoded query from ai_graph.py. The quiz_score is randomly generated for demonstration.*

## 📂 File Structure

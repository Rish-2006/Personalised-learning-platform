# Personalized Learning Platform

An AI-powered, production-ready web application designed to deliver customized learning experiences. This platform leverages AI to generate, adapt, and present educational content tailored to user needs. It features an independent frontend and backend architecture, ready to be deployed on Vercel and Render respectively.

## ✨ Key Features

- **🤖 AI-Powered Lesson Generation**: Dynamically creates comprehensive lesson plans on any given topic using the Gemini AI model.
- **🔐 User Authentication**: Secure user registration and login system with password hashing using bcrypt.
- **📝 Automated Assessments & Revision**: Generates practice quizzes and concise revision notes based on the dynamically created lesson content.
- **⚙ Modular Architecture**: Independent frontend and backend for seamless, decoupled deployments.
- **🖥 Interactive UI**: A clean, responsive user interface built with HTML, CSS, and Vanilla JavaScript.

## 🏛 Architecture Overview

The application follows a client-server architecture, enabling decoupled deployment:

1. **Frontend (Vercel)**: A lightweight, static SPA (Single Page Application) built with pure HTML, CSS, and JS. It communicates directly with the backend API.
2. **Backend (Render)**: A RESTful API built with Flask, SQLAlchemy, and Gunicorn. It handles authentication, database interactions, and integrations with the Google Gemini AI model.
3. **Database**: SQLite (default for development) or PostgreSQL (configured via environment variables for production), managed through Flask-SQLAlchemy.

---

## ⚙ Prerequisites & Environment Variables

### System Requirements
- Python 3.8+
- Node.js & npm (optional, if you plan to use Vercel CLI)
- Git

### Environment Variables (.env)
You will need to set up the following environment variables in your backend to ensure everything functions properly.

| Variable Name | Description | Default / Example |
|---------------|-------------|-------------------|
| `GOOGLE_API_KEY` | Your Google Gemini API Key for AI features | `AIzaSyYourApiKeyHere...` |
| `DATABASE_URL` | Connection string for your database (optional) | `sqlite:///learning_platform.db` |

---

## 🚀 Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/personalized-learning-platform.git
cd personalized-learning-platform
```

### 2. Backend Setup
```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your Google API Key
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env

# Start the Flask backend
python app.py
```
*The backend API will run at `http://127.0.0.1:5000`.*

### 3. Frontend Setup
```bash
# Open a new terminal window
cd frontend

# Open index.html in your browser, or use a local server:
npx serve .
```

---

## 🌍 Deployment Guide

This project is configured for split deployment: **Frontend on Vercel** and **Backend on Render**.

### Phase 1: Deploy Backend to Render

1. Go to [Render](https://render.com/) and create a new **Web Service**.
2. Connect your GitHub repository and select the `backend` directory (if Render supports root directories, set the Root Directory to `backend`).
3. Set the following configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Go to the **Environment** tab and add your variables:
   - `GOOGLE_API_KEY`: Your Gemini API Key.
   - `PYTHON_VERSION`: `3.10.0` (or your preferred Python version).
5. Click **Deploy**. Once successful, copy the provided Render URL (e.g., `https://your-backend.onrender.com`).

### Phase 2: Deploy Frontend to Vercel

1. Open `frontend/script.js` in your text editor.
2. Locate the `API_URL` configuration at the top of the file.
3. Replace the placeholder URL with your actual deployed Render backend URL:
   ```javascript
   const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
       ? 'http://127.0.0.1:5000' 
       : 'https://your-backend.onrender.com'; // <-- REPLACE THIS
   ```
4. Commit and push this change to your repository.
5. Go to [Vercel](https://vercel.com/) and click **Add New > Project**.
6. Import your GitHub repository.
7. In the configuration, set the **Root Directory** to `frontend`.
8. Leave the Build Command and Output Directory as default (Vercel will detect static files).
9. Click **Deploy**. Your frontend is now live and communicating with your backend!

---

## 📂 Project Structure

```text
personalized-learning-platform/
├── backend/
│   ├── app.py               # Main Flask application and API routes
│   ├── database.py          # SQLAlchemy database models
│   ├── requirements.txt     # Python dependencies (includes gunicorn for Render)
│   └── ...
├── frontend/
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Main application interface
│   ├── script.js            # Frontend logic and API communication
│   ├── style.css            # Stylesheets
│   └── ...
└── README.md                # Project documentation
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

# Copilot Instructions for Personalised Learning Platform

## Project Overview
- **Monorepo structure**: Contains `backend/` (Python, FastAPI/Flask style) and `frontend/` (HTML/CSS/JS) directories.
- **Backend**: Handles AI logic, authentication, database, and API endpoints. Key files:
  - `ai_crew.py`, `ai_graph.py`: AI logic and orchestration
  - `app.py`: Main API entry point
  - `auth.py`: Authentication logic
  - `database.py`: Database access and models
  - `requirements.txt`: Python dependencies
- **Frontend**: Static HTML/CSS/JS for user interface. Key files:
  - `index.html`, `dashboard.html`, `lesson.html`, `login.html`: Main pages
  - `script.js`: Handles client-side logic and API calls
  - `style.css`: Project-wide styling

## Key Patterns & Conventions
- **API communication**: Frontend JS (`script.js`) communicates with backend via HTTP endpoints defined in `app.py`.
- **AI logic**: Centralized in `ai_crew.py` and `ai_graph.py`. These files may define workflows, agents, or graph-based logic for personalized learning.
- **Authentication**: Managed in `auth.py`, likely using JWT or session tokens. Secure endpoints accordingly.
- **Database**: Accessed via `database.py`. Use provided functions/classes for DB operations—avoid direct SQL in other files.
- **Frontend**: No frameworks; vanilla JS and HTML. Use `script.js` for all dynamic behavior and API calls.

## Developer Workflows
- **Backend**: Run with `python app.py` from `backend/` directory. Ensure dependencies from `requirements.txt` are installed.
- **Frontend**: Open HTML files directly or serve via a simple HTTP server for local development.
- **Testing**: No explicit test files found—add tests in `backend/` as needed, following Python conventions.
- **Debugging**: Use print/logging in backend Python files; use browser dev tools for frontend JS.

## Integration & Dependencies
- **Python packages**: All backend dependencies listed in `backend/requirements.txt`.
- **No build step**: Static frontend, interpreted backend—no transpilation or bundling required.

## Examples
- To add a new API endpoint: define in `app.py`, implement logic in a relevant backend file, and call from `script.js`.
- To add a new page: create an HTML file in `frontend/`, link to `script.js` and `style.css` as needed.

## Tips for AI Agents
- Respect the separation between backend (Python) and frontend (HTML/JS).
- Reuse existing utility functions and patterns from `database.py`, `auth.py`, and AI modules.
- Follow the file structure and naming conventions for new features.
- Document any new endpoints or workflows clearly in code comments.

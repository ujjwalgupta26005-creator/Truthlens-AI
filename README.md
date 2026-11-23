# TruthLens AI

TruthLens AI is a web application that helps users analyze potentially misleading news content using text or image input. It uses Google's Gemini API to generate an AI-assisted analysis and SQLite to keep a local history.

> **Important:** AI output is not proof that a claim is true or false. Independently verify important claims using reliable sources.

## Features
- Text analysis
- Image analysis
- AI-generated explanation and warning signs
- SQLite analysis history
- View and delete saved history

## Technology
- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI, Uvicorn
- AI: Google Gemini API (`google-genai`)
- Database: SQLite

## Setup

1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your own Gemini API key:

   ```env
   GEMINI_API_KEY=your_real_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

5. Start the backend from the project root:

   ```bash
   uvicorn backend.main:app --reload
   ```

6. Open `frontend/index.html` in a browser. The backend should be running at `http://127.0.0.1:8000`.

## API endpoints
- `GET /` — health/status
- `POST /analyze-text` — analyze text
- `POST /analyze-image` — analyze an uploaded image
- `GET /history` — retrieve saved analyses
- `DELETE /history/{history_id}` — delete one history item

## Security
- Never upload `.env` or your real API key to GitHub.
- `.env` is excluded through `.gitignore`.
- Do not commit private user data or database files.

## Note
This is a GitHub-ready starter implementation based on the described TruthLens AI architecture. Compare it with your team's actual project before submitting it as the team's original source code.

Backend (FastAPI + SQLite)

1) Create venv (Windows)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2) Install dependencies
   pip install -r requirements.txt

3) Run API (localhost)
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Health check:
  GET http://127.0.0.1:8000/health

Uploads:
  backend/uploads/

SQLite DB:
  backend/app.db

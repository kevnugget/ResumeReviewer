# AI Resume Reviewer

**Domain:** Artificial Intelligence / Natural Language Processing / Career Tools

**Team Members:**
- Kevin Nguyen

---

## Overview

AI Resume Reviewer is a full-stack web application that analyzes a student's resume section by section using a Retrieval-Augmented Generation (RAG) pipeline backed by Google Gemini. Users upload or paste their resume, optionally fill in a persistent profile (career stage, target role, goals), and receive specific, actionable feedback per section. A follow-up Q&A panel lets users ask career questions grounded in their resume.

---

## Architecture

### Data Flow

```
User (Browser)
  │
  │  1. Fill profile (saved to localStorage — persists across sessions)
  │  2. Upload file (.pdf / .docx / .txt) or paste resume text
  │  3. POST /review  (multipart/form-data: file|text + profile JSON)
  ▼
FastAPI Backend  (port 8000)
  │
  ├── parser.py
  │     PyMuPDF   → extracts text from PDF
  │     python-docx → extracts text from DOCX
  │     UTF-8 decode → plain TXT
  │
  ├── partitioner.py
  │     Regex splits plain text into labeled sections:
  │     experience · education · skills · projects · certifications · other
  │
  ├── rag.py  (runs once per section)
  │     TF-IDF vectorizer (scikit-learn) encodes the section text
  │     Cosine similarity retrieves top-3 relevant tips from a
  │     hardcoded knowledge base (~20 best-practice tips per section)
  │
  ├── reviewer.py  (runs once per section)
  │     Builds prompt:  profile context + RAG tips + section text
  │     Calls Gemini API (gemini-2.5-flash → fallback gemini-2.0-flash)
  │     Exponential backoff retry on 503 / high-demand errors
  │     Returns 3-5 bullet-point feedback string per section
  │
  └── JSON response  →  { sections: { experience: "...", education: "...", ... } }
        │
        ▼
React Frontend  (port 5173)
  Renders one feedback card per section
  Follow-up Q&A: POST /ask  (question + full resume text + profile)
```

### File Map

```
ResumeReviewer/
├── backend/
│   ├── app.py            # FastAPI routes (/review, /ask)
│   ├── parser.py         # File-to-text extraction (PDF, DOCX, TXT)
│   ├── partitioner.py    # Section detection via regex header matching
│   ├── reviewer.py       # LLM prompting, retry/fallback, input guardrails
│   ├── rag.py            # TF-IDF knowledge base and retrieval
│   ├── requirements.txt
│   └── .env              # ← NOT committed (see setup below)
└── frontend/
    ├── src/
    │   ├── App.jsx        # Full UI: profile card, upload, feedback, Q&A
    │   └── main.jsx
    └── package.json
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google AI Studio API key — get one free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

### 1. Backend

```bash
cd ResumeReviewer/backend
```

**Create and activate a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Create the `.env` file** (never commit this file):

```
# ResumeReviewer/backend/.env
GOOGLE_API_KEY=your_google_api_key_here
```

**Start the server:**

```bash
uvicorn app:app --reload
```

API is available at `http://localhost:8000`.

---

### 2. Frontend

Open a second terminal:

```bash
cd ResumeReviewer/frontend
npm install
npm run dev
```

App is available at `http://localhost:5173`.

---

## Environment Variables

| Variable | File | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | `backend/.env` | Authenticates requests to the Google Gemini API |

**Security rules:**
- `.env` files must **never** be committed to the repository.
- Ensure `backend/.env` is listed in `.gitignore`.
- Never hard-code API keys in source files.

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| TF-IDF RAG (no vector DB) | Self-contained with zero infrastructure; the knowledge base is small enough that in-memory similarity search is instant |
| Gemini 2.5 Flash + 2.0 Flash fallback | Balances quality and cost; automatic fallback handles API demand spikes (503 errors) |
| Profile stored in localStorage | No backend database or login required; data persists across sessions automatically |
| Guardrails inside the LLM prompt | Enforcing topic scope in the system instruction is simpler and more robust than keyword blocklists |
| Resume validation via keyword heuristic | Catches obviously wrong input (random text) without an extra API call |

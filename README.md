# AI Resume Reviewer

A fullstack web app that lets users upload a resume and receive section-by-section AI feedback powered by Google Gemini and a RAG pipeline.

## Features

- Upload a resume as PDF, DOCX, or TXT — or paste the text directly
- Automatically partitions the resume into sections (Experience, Education, Skills, Projects, etc.)
- Retrieves relevant best-practice tips per section using TF-IDF RAG
- Sends each section + retrieved tips to Gemini for targeted, actionable feedback
- Flags summary sections and recommends removing them
- Follow-up question box so users can ask the LLM anything about their resume

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React, Vite |
| Backend | FastAPI, Python |
| LLM | Google Gemini (gemini-2.5-flash) |
| RAG | scikit-learn TF-IDF + cosine similarity |
| PDF parsing | PyMuPDF |
| DOCX parsing | python-docx |

## Project Structure

```
ResumeReviewer/
├── backend/
│   ├── app.py          # FastAPI routes
│   ├── parser.py       # PDF/DOCX/TXT text extraction
│   ├── partitioner.py  # splits resume into sections
│   ├── rag.py          # TF-IDF retrieval of best-practice tips
│   ├── reviewer.py     # Gemini API calls
│   ├── .env            # API key (not committed)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx     # main UI
    │   └── index.css
    └── package.json
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Google Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Backend

```powershell
cd backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
GOOGLE_API_KEY=your_key_here
```

Start the server:
```powershell
uvicorn app:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173`
2. Upload a resume file or paste resume text
3. Click **Review My Resume**
4. Read the per-section feedback
5. Use the follow-up question box to ask anything about your resume

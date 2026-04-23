import os
import time
from datetime import date
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from rag import retrieve

load_dotenv()  # load GEMINI_API_KEY from .env

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

_RESUME_KEYWORDS = {
    "experience", "education", "skills", "work", "employment",
    "university", "college", "degree", "gpa", "internship",
    "projects", "certifications", "objective", "summary", "linkedin",
    "github", "responsibilities", "achievements", "qualifications",
    "position", "company", "bachelor", "master", "phd", "resume", "cv",
}

def is_valid_resume(text):
    if len(text.strip()) < 100:
        return False
    lower = text.lower()
    matches = sum(1 for kw in _RESUME_KEYWORDS if kw in lower)
    return matches >= 3


def _generate_with_retry(prompt):
    """Try each model in order; retry once with backoff on 503."""
    for model in _MODELS:
        for attempt in range(3):
            try:
                return client.models.generate_content(model=model, contents=prompt)
            except genai_errors.ServerError as e:
                if e.code == 503 and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                break  # non-503 or exhausted retries — try next model
    raise RuntimeError("All Gemini models unavailable. Please try again later.")


def review_sections(sections):
    feedback = {}

    for section_name, section_text in sections.items():
        if not section_text.strip():
            continue

        # if the resume has a summary section, flag it instead of reviewing it
        if section_name == "summary":
            feedback[section_name] = (
                "Consider removing this summary section. "
                "Recruiters rarely read them and the space is better used for experience or projects."
            )
            continue

        tips = retrieve(section_name, section_text)  # get relevant best-practice tips from RAG
        tips_text = "\n".join(f"- {t}" for t in tips)

        today = date.today().strftime("%B %d, %Y")  # e.g. April 19, 2026

        prompt = f"""You are a resume reviewer helping a college student improve their resume.
Today's date is {today}. Use this to correctly judge whether dates on the resume are past, current, or future.

Review the following '{section_name}' section and give specific, actionable feedback.
Keep your response to 3-5 bullet points. Be direct and constructive.

Relevant best practices to consider:
{tips_text}

Resume section:
{section_text}

Feedback:"""

        response = _generate_with_retry(prompt)
        feedback[section_name] = response.text.strip()

    return feedback


def ask_question(question, resume_context):
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""You are a resume advisor helping a college student. You only answer questions about resumes, career advice, job applications, and professional development.
Today's date is {today}.

If the question is not related to resumes, careers, or job applications, respond with exactly:
"Please ask a question related to your resume."

The student's resume is below for context:
{resume_context}

The student asks: {question}

Give a helpful, specific answer in 2-4 sentences."""

    response = _generate_with_retry(prompt)
    return response.text.strip()

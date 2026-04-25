import os
import json
import time
from datetime import date
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from rag import retrieve

load_dotenv(override=True)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

_MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]

_RESUME_KEYWORDS = {
    "experience", "education", "skills", "work", "employment",
    "university", "college", "degree", "gpa", "internship",
    "projects", "certifications", "objective", "summary", "linkedin",
    "github", "responsibilities", "achievements", "qualifications",
    "position", "company", "bachelor", "master", "phd", "resume", "cv",
}

def _format_profile(profile_json):
    if not profile_json:
        return ""
    try:
        p = json.loads(profile_json)
        parts = []
        if p.get("careerStage"):   parts.append(f"Career stage: {p['careerStage']}")
        if p.get("targetRole"):    parts.append(f"Target role: {p['targetRole']}")
        if p.get("targetIndustry"):parts.append(f"Target industry: {p['targetIndustry']}")
        if p.get("goals"):         parts.append(f"Career goals: {p['goals']}")
        return "\n".join(parts)
    except (json.JSONDecodeError, TypeError):
        return ""


def is_valid_resume(text):
    if len(text.strip()) < 100:
        return False
    lower = text.lower()
    matches = sum(1 for kw in _RESUME_KEYWORDS if kw in lower)
    return matches >= 3


def _generate_with_retry(prompt):
    """Try each model in order; retry with backoff on 503, skip to next model on 429."""
    rate_limited = 0
    for model in _MODELS:
        for attempt in range(3):
            try:
                return client.models.generate_content(model=model, contents=prompt)
            except genai_errors.ClientError as e:
                if e.code in (429, 404):
                    if e.code == 429:
                        rate_limited += 1
                    print(f"[reviewer] {model} unavailable ({e.code}), trying next model...")
                    break  # skip to next model
                raise  # other 4xx errors are caller bugs, propagate immediately
            except genai_errors.ServerError as e:
                if e.code == 503 and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                break  # non-503 or exhausted retries — try next model
    if rate_limited == len(_MODELS):
        raise RuntimeError(
            "Daily quota exceeded for all available Gemini models. "
            "Please try again tomorrow or upgrade your Google AI plan."
        )
    raise RuntimeError("All Gemini models unavailable. Please try again later.")


def review_sections(sections, profile_json=""):
    feedback = {}
    profile_text = _format_profile(profile_json)
    profile_block = f"\nAbout the candidate:\n{profile_text}\n" if profile_text else ""

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
{profile_block}
Review the following '{section_name}' section and give specific, actionable feedback tailored to the candidate's background and goals above.
Keep your response to 3-5 bullet points. Be direct and constructive.

Here is an example of the feedback format you should follow:

Example resume bullet: "Responsible for helping with website development and fixing bugs"
Example feedback:
• **Weak action verb** — replace "Responsible for helping" with a direct verb like "Built" or "Debugged" to show ownership.
• **No measurable impact** — add a specific outcome, e.g. "Reduced bug backlog by 30% over two sprints."

Always use this format: • **Short label** — one sentence of specific, actionable advice.

Relevant best practices to consider:
{tips_text}

Resume section to review:
{section_text}

Feedback:"""

        response = _generate_with_retry(prompt)
        feedback[section_name] = response.text.strip()

    return feedback


def ask_question(question, resume_context, profile_json="", history_json=""):
    today = date.today().strftime("%B %d, %Y")
    profile_text = _format_profile(profile_json)
    profile_block = f"\nAbout the candidate:\n{profile_text}\n" if profile_text else ""

    history_block = ""
    if history_json:
        try:
            history = json.loads(history_json)
            if history:
                turns = "\n\n".join(
                    f"Student: {t['question']}\nAdvisor: {t['answer']}"
                    for t in history
                )
                history_block = f"\nPrevious conversation:\n{turns}\n"
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    prompt = f"""You are a resume advisor helping a college student. You only answer questions about resumes, career advice, job applications, and professional development.
Today's date is {today}.
{profile_block}
If the question is not related to resumes, careers, or job applications, respond with exactly:
"Please ask a question related to your resume."

The student's resume is below for context:
{resume_context}
{history_block}
The student asks: {question}

Give a helpful, specific answer in 2-4 sentences."""

    response = _generate_with_retry(prompt)
    return response.text.strip()

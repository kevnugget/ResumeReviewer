import os
from datetime import date
from google import genai
from dotenv import load_dotenv
from rag import retrieve

load_dotenv()  # load GEMINI_API_KEY from .env

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


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

        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        feedback[section_name] = response.text.strip()

    return feedback

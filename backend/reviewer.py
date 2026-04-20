import os
import google.generativeai as genai
from dotenv import load_dotenv
from rag import retrieve

load_dotenv()  # load GEMINI_API_KEY from .env

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


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

        prompt = f"""You are a resume reviewer helping a college student improve their resume.

Review the following '{section_name}' section and give specific, actionable feedback.
Keep your response to 3-5 bullet points. Be direct and constructive.

Relevant best practices to consider:
{tips_text}

Resume section:
{section_text}

Feedback:"""

        response = model.generate_content(prompt)
        feedback[section_name] = response.text.strip()

    return feedback

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# knowledge base of resume best-practice tips, grouped by section
TIPS = {
    "experience": [
        "start each bullet point with a strong action verb like led, built, or improved",
        "quantify achievements with numbers, percentages, or dollar amounts",
        "focus on impact and results, not just what your responsibilities were",
        "keep bullet points to one or two lines, avoid long paragraphs",
        "tailor your experience descriptions to match the job you are applying for",
        "list jobs in reverse chronological order, most recent first",
    ],
    "education": [
        "include your gpa if it is 3.5 or higher",
        "list relevant coursework if you do not have much work experience",
        "include graduation date or expected graduation date",
        "put education near the top if you are a recent graduate",
    ],
    "skills": [
        "group skills into categories like languages, frameworks, and tools",
        "only list skills you can actually speak to in an interview",
        "avoid listing soft skills like teamwork or communication, show them through experience instead",
        "keep the skills section concise and scannable",
    ],
    "projects": [
        "include a link to the project or github repo if possible",
        "describe the problem the project solved, not just the technologies used",
        "mention your specific contribution if it was a group project",
        "quantify impact if possible, such as number of users or performance improvements",
    ],
    "certifications": [
        "include the issuing organization and the date you earned it",
        "only list certifications that are relevant to the role you are applying for",
    ],
    "other": [
        "keep the resume to one page if you have less than ten years of experience",
        "use a clean consistent font and layout with enough white space",
        "avoid photos, graphics, or tables that may break applicant tracking systems",
        "proofread carefully, spelling mistakes are an easy way to get screened out",
    ],
}

# flatten all tips into one list so we can vectorize them together
ALL_TIPS = [(section, tip) for section, tips in TIPS.items() for tip in tips]
TIP_TEXTS = [tip for _, tip in ALL_TIPS]

# fit the vectorizer on the full tip library once at startup
vectorizer = TfidfVectorizer()
tip_vectors = vectorizer.fit_transform(TIP_TEXTS)


def retrieve(section_name, section_text, top_k=3):
    # combine section name and text so the query captures context from both
    query = f"{section_name} {section_text}"
    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(query_vector, tip_vectors)[0]  # score every tip against this section
    top_indices = scores.argsort()[-top_k:][::-1]  # grab indices of the top k highest scores

    return [TIP_TEXTS[i] for i in top_indices]  # return the actual tip strings

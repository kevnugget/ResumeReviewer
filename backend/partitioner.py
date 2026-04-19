import re

# keywords that signal the start of a new resume section
SECTION_HEADERS = {
    "summary": ["summary", "objective", "profile", "about me"],
    "experience": ["experience", "work experience", "employment", "work history"],
    "education": ["education", "academic background", "degrees"],
    "skills": ["skills", "technical skills", "technologies", "competencies"],
    "projects": ["projects", "personal projects", "portfolio"],
    "certifications": ["certifications", "certificates", "licenses"],
}


def partition(resume_text):
    sections = {}
    current_section = "other"
    sections[current_section] = []

    for line in resume_text.splitlines():
        matched = match_header(line.strip().lower())
        if matched:
            current_section = matched  # start collecting under the new section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)  # add line to whatever section we're in

    # join each section's lines back into a single string and drop empty ones
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def match_header(line):
    for section, keywords in SECTION_HEADERS.items():
        for keyword in keywords:
            if re.fullmatch(keyword + r"[:\s]*", line):  # match lines that are just a header label
                return section
    return None

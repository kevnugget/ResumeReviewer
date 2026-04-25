import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_KB_PATH = Path(__file__).parent / "data" / "knowledge_base.json"
TIPS = json.loads(_KB_PATH.read_text(encoding="utf-8"))

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

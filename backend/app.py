from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser import extract_text
from partitioner import partition
from reviewer import review_sections, ask_question, is_valid_resume

app = FastAPI()

# let the react frontend on port 5173 talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Resume Reviewer API is running"}

@app.post("/review")
async def review_resume(
    file: UploadFile = File(default=None),
    text: str = Form(default=""),
    profile: str = Form(default=""),
):
    if not file and not text.strip():
        raise HTTPException(status_code=400, detail="Please provide a file or resume text.")

    if file:
        raw_bytes = await file.read()
        resume_text = extract_text(raw_bytes, file.filename)  # convert to plain text based on file type
    else:
        if not is_valid_resume(text):
            raise HTTPException(status_code=422, detail="That doesn't look like a resume. Please paste your actual resume content.")
        resume_text = text

    sections = partition(resume_text)  # split resume into labeled sections
    feedback = review_sections(sections, profile)  # get LLM feedback per section using RAG context

    return {
        "sections": feedback,
        "overall": f"Reviewed {len(feedback)} sections."
    }


@app.post("/ask")
async def ask(
    question: str = Form(...),
    context: str = Form(default=""),
    profile: str = Form(default=""),
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Please enter a question.")

    answer = ask_question(question, context, profile)
    return {"answer": answer}

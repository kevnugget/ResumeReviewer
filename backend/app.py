from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser import extract_text
from partitioner import partition
from reviewer import review_sections

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
    text: str = Form(default="")
):
    if not file and not text.strip():
        raise HTTPException(status_code=400, detail="Please provide a file or resume text.")

    if file:
        raw_bytes = await file.read() 
        resume_text = extract_text(raw_bytes, file.filename)  # convert to plain text based on file type
    else:
        resume_text = text  # user pasted text directly, use it as-is

    sections = partition(resume_text)  # split resume into labeled sections
    feedback = review_sections(sections)  # get LLM feedback per section using RAG context

    return {
        "sections": feedback,
        "overall": f"Reviewed {len(feedback)} sections."
    }

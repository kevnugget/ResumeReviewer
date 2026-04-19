from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

    # Placeholder - will wire in parser, partitioner, RAG, and LLM next
    return {
        "sections": {},
        "overall": "Backend connected! Parser coming next."
    }

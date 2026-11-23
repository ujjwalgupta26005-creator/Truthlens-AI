import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from PIL import Image

from .database import init_db, save_analysis, get_history, delete_history

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="TruthLens AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For a public deployment, replace with your frontend domain.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

class TextRequest(BaseModel):
    text: str = Field(min_length=5, max_length=10000)

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured on the server.")
    return genai.Client(api_key=api_key)

def ask_gemini(contents):
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = (
        "You are an assistant helping users critically examine news claims. "
        "Analyze the supplied content. Do not claim certainty without evidence. "
        "Return: (1) a cautious assessment such as potentially misleading, appears plausible, "
        "or insufficient information, (2) a short summary, (3) warning signs, and "
        "(4) what a user should independently verify. Clearly state that this is not a verified fact-check."
    )
    try:
        response = get_client().models.generate_content(
            model=model,
            contents=[prompt, *contents] if isinstance(contents, list) else [prompt, contents],
        )
        return response.text or "The AI model returned an empty response."
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {str(exc)}")

@app.get("/")
def health():
    return {"status": "ok", "message": "TruthLens AI backend is running"}

@app.post("/analyze-text")
def analyze_text(payload: TextRequest):
    result = ask_gemini(payload.text)
    record_id = save_analysis("text", payload.text, result)
    return {"id": record_id, "input_type": "text", "analysis": result}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Please upload a JPG, PNG, or WEBP image.")
    raw = await file.read()
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 8 MB or smaller.")
    try:
        image = Image.open(BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.")
    result = ask_gemini([image])
    record_id = save_analysis("image", file.filename or "uploaded image", result)
    return {"id": record_id, "input_type": "image", "analysis": result}

@app.get("/history")
def history():
    return {"history": get_history()}

@app.delete("/history/{history_id}")
def remove_history(history_id: int):
    deleted = delete_history(history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History item not found.")
    return {"message": "History item deleted"}

import os
from typing import Optional, List
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.storage import GrievanceStore
from app.models.schemas import GrievanceCreate, Channel

app = FastAPI(
    title="NagrikSetu AI — CivicPulse Tricity",
    description="Multilingual AI Digital Public Infrastructure Platform for Chandigarh, Mohali, and Panchkula.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage and template directories
store = GrievanceStore()

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

class StatusUpdate(BaseModel):
    status: str

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    grievances = store.get_all()
    hotspots = store.get_hotspots()
    sector_metrics = store.get_sector_metrics()
    recommendations = store.get_policy_recommendations()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "grievances": grievances,
            "hotspots": hotspots,
            "sector_metrics": sector_metrics,
            "recommendations": recommendations,
            "total_count": len(grievances)
        }
    )

@app.get("/presentation", response_class=HTMLResponse)
async def serve_presentation():
    presentation_file = os.path.join(os.path.dirname(__file__), "..", "presentation", "index.html")
    if os.path.exists(presentation_file):
        with open(presentation_file, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="Presentation deck not found")

@app.get("/api/v1/grievances")
async def list_grievances(sector: Optional[str] = None, category: Optional[str] = None, channel: Optional[str] = None):
    return store.get_all(sector=sector, category=category, channel=channel)

@app.get("/api/v1/grievances/{grievance_id}")
async def get_grievance(grievance_id: str):
    item = store.get_by_id(grievance_id)
    if not item:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return item

@app.post("/api/v1/grievances")
async def create_grievance(payload: GrievanceCreate):
    record = store.add_grievance(
        raw_input=payload.raw_input,
        channel=payload.channel.value if hasattr(payload.channel, 'value') else str(payload.channel),
        audio_file=payload.audio_file_name,
        location_hint=payload.location_hint
    )
    return record

@app.post("/api/v1/voice/upload")
async def upload_voice(
    file: UploadFile = File(...),
    transcript: Optional[str] = Form(None),
    location_hint: Optional[str] = Form(None)
):
    """
    Accepts audio recording from mobile or browser.
    Saves audio file and triggers Google Gemini speech/multimodal analysis.
    """
    file_path = os.path.join(uploads_dir, file.filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Use provided transcript or simulated voice transcription
    text_content = transcript or "ਸਾਡੇ ਸੈਕਟਰ 22 ਸ਼ਾਸਤਰੀ ਮਾਰਕੀਟ ਕੋਲ ਪਾਣੀ ਦੀ ਲੀਕੇਜ ਹੋ ਰਹੀ ਹੈ"

    record = store.add_grievance(
        raw_input=text_content,
        channel="VOICE",
        audio_file=file.filename,
        location_hint=location_hint
    )
    return record

@app.post("/api/v1/grievances/{grievance_id}/upvote")
async def upvote_grievance(grievance_id: str):
    res = store.upvote(grievance_id)
    if not res:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return res

@app.patch("/api/v1/grievances/{grievance_id}/status")
async def update_grievance_status(grievance_id: str, payload: StatusUpdate):
    res = store.update_status(grievance_id, payload.status)
    if not res:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return res

@app.get("/api/v1/hotspots")
async def get_hotspots():
    return store.get_hotspots()

@app.get("/api/v1/sectors")
async def get_sectors():
    return store.get_sector_metrics()

@app.get("/api/v1/recommendations")
async def get_recommendations():
    return store.get_policy_recommendations()

@app.post("/api/v1/webhook/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form("whatsapp:+919876543210")):
    """
    Twilio/WhatsApp webhook simulating citizen messaging interface.
    """
    record = store.add_grievance(
        raw_input=Body,
        channel="WHATSAPP",
        location_hint=None
    )
    return {
        "status": "success",
        "reply": f"Dhanyavaad! Your grievance has been recorded under {record['id']} ({record['category']} - {record['sector']}). Status: {record['status']}."
    }

@app.get("/api/v1/stats")
async def get_stats():
    grievances = store.get_all()
    by_category = {}
    by_channel = {}
    by_language = {}
    total_urgency = 0

    for g in grievances:
        cat = g.get("category", "Other")
        ch = g.get("channel", "WEB")
        lang = g.get("language_detected", "English")
        by_category[cat] = by_category.get(cat, 0) + 1
        by_channel[ch] = by_channel.get(ch, 0) + 1
        by_language[lang] = by_language.get(lang, 0) + 1
        total_urgency += g.get("urgency_score", 5)

    return {
        "total_grievances": len(grievances),
        "avg_urgency": round(total_urgency / max(1, len(grievances)), 1),
        "by_category": by_category,
        "by_channel": by_channel,
        "by_language": by_language,
        "active_hotspots_count": len(store.get_hotspots()),
        "dpr_recommendations_count": len(store.get_policy_recommendations())
    }

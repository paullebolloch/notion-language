from fastapi import FastAPI, Request, Query
from app.notion import notion_health, debug_flashcards, add_study_session, get_random_flashcard, update_flashcard_stats
from datetime import datetime
import random
from typing import Optional

app = FastAPI(title="Notion Language Lab")

# Health Check Endpoint
@app.get("/")
def home():
    return {"ok": True, "msg": "Server operational ✅"}

@app.get("/health/notion")
def health_notion():
    return notion_health()

@app.get("/debug/flashcards")
def debug_flashcards_meta(limit: int = 3):
    return debug_flashcards(limit)

# Basic Endpoints
@app.post("/timer/start")
def start_timer():
    start_time = datetime.utcnow().isoformat()
    add_study_session(start_time=start_time)
    return {"status": "started", "start_time": start_time}

@app.post("/timer/stop")
def stop_timer():
    end_time = datetime.utcnow().isoformat()
    add_study_session(end_time=end_time)
    return {"status": "stopped", "end_time": end_time}

@app.get("/flashcards/random")
def random_flashcard(request: Request, language: Optional[str] = Query(None, description="Language filter")):
    card = get_random_flashcard(language=language)
    
    print("DEBUG endpoint card:", card, flush=True)

    if "error" in card:
        return card  
    
    return {
    "Front": card["Front"],
    "Back": card["Back"],
    "id": card["id"]
}

@app.post("/flashcards/update")
def update_flashcard(id: str = Query(...), success: bool = Query(...)):
    result = update_flashcard_stats(id, success)
    return result

# Run the app
# uvicorn app.main:app --reload --port 8000 
# ngrok http 8000 (dans un autre terminal)
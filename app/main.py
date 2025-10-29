from fastapi import FastAPI
from app.notion import notion_health, debug_flashcards, add_study_session, get_random_flashcard 
from datetime import datetime
import random

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
def random_flashcard():
    card = get_random_flashcard()
    return {"front": card["Front"], "back": card["Back"]}
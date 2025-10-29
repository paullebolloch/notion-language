from notion_client import Client
from notion_client.errors import APIResponseError
from app.config import NOTION_TOKEN, DB_FLASHCARDS, DB_SESSIONS
from typing import Dict, Any
import random
from datetime import datetime, timezone


notion = Client(
    auth=NOTION_TOKEN,
    notion_version="2025-09-03" # Required for the new multi-source database API
)


def notion_health():
    try:
        meta = notion.databases.retrieve(DB_FLASHCARDS)
        title = "".join([t["plain_text"] for t in meta.get("title", [])])
        return {"ok": True, "database_title": title}
    except APIResponseError as e:
        return {"ok": False, "error_code": e.code, "error": str(e)}


def debug_flashcards(limit: int = 3) -> Dict[str, Any]:
    """
    Fetch a sample of pages from a multi-source Notion database (API version 2025-09-03).
    This function demonstrates how to query a specific data source within a database.
    """
    # Step 1: Retrieve database metadata and extract the first data source ID
    db_meta = notion.databases.retrieve(DB_FLASHCARDS)
    data_sources = db_meta.get("data_sources", [])
    if not data_sources:
        return {"error": "No data sources found. Ensure your database uses the new Notion API."}

    data_source_id = data_sources[0]["id"]

    # Step 2: Query the data source directly through the API
    res = notion.request(
        path=f"/data_sources/{data_source_id}/query",
        method="POST",
        body={"page_size": limit}
    )

    pages = res.get("results", [])
    sample_titles = []

    # Step 3: Extract the title property for each page (regardless of its field name)
    for page in pages:
        props = page.get("properties", {}) or {}
        title_key = next((k for k, v in props.items() if v.get("type") == "title"), None)
        if title_key:
            title_blocks = props[title_key].get("title", []) or []
            title_text = title_blocks[0]["plain_text"] if title_blocks else ""
        else:
            title_text = ""
        sample_titles.append({
            "page_id": page.get("id", ""),
            "title_key": title_key,
            "title_text": title_text
        })

    # Step 4: Return a clean JSON response
    return {
        "data_source_id": data_source_id,
        "page_count": len(pages),
        "sample_titles": sample_titles
    }

def _get_data_source_id(database_id: str) -> str:
    """Retrieve the first data_source_id for a given database."""
    db_meta = notion.databases.retrieve(database_id)
    sources = db_meta.get("data_sources", [])
    if not sources:
        raise ValueError("No data sources found for this database.")
    return sources[0]["id"]

def to_utc(dt_str: str) -> datetime:
    """Convert any ISO 8601 string (with or without timezone info) to a UTC datetime."""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

def _find_active_session(data_source_id: str) -> dict | None:
    """Return the latest session with Status == 'Started'."""
    res = notion.request(
        path=f"/data_sources/{data_source_id}/query",
        method="POST",
        body={
            "filter": {
                "property": "Status",
                "select": {"equals": "Started"}
            },
            "sorts": [{"property": "Start Time", "direction": "descending"}],
            "page_size": 1
        }
    )
    results = res.get("results", [])
    return results[0] if results else None


def add_study_session(start_time: str = None, end_time: str = None) -> dict:
    """Start or stop a study session depending on provided params."""
    data_source_id = _get_data_source_id(DB_SESSIONS)

    # ─── START SESSION ───────────────────────────────────────────────
    if start_time and not end_time:
        active = _find_active_session(data_source_id)
        if active:
            return {"ok": False, "error": "A session is already active."}

        payload = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": {
                            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Spanish Session"}
                    }
                ]
            },
                "Activity": {"select": {"name": "Flashcard"}},
                "Language": {"select": {"name": "Spanish"}},
                "Start Time": {"date": {"start": start_time}},
                "Status": {"select": {"name": "Started"}}
            }
        }
        notion.pages.create(**payload)
        return {"ok": True, "status": "started", "start_time": start_time}

    # ─── STOP SESSION ────────────────────────────────────────────────
    elif end_time and not start_time:
        active = _find_active_session(data_source_id)
        if not active:
            return {"ok": False, "error": "No active session found to stop."}

        page_id = active["id"]
        start_value = active["properties"]["Start Time"]["date"]["start"]
        dt_start = to_utc(start_value)
        dt_end = to_utc(end_time)
        duration = round((dt_end - dt_start).total_seconds() / 60, 0)

        update_payload = {
            "properties": {
                "End Time": {"date": {"start": end_time}},
                "Duration (min)": {"number": duration},
                "Status": {"select": {"name": "Stopped"}}
            }
        }

        notion.pages.update(page_id=page_id, **update_payload)
        return {"ok": True, "status": "stopped", "duration_min": duration}

    # ─── INVALID USAGE ───────────────────────────────────────────────
    else:
        return {"ok": False, "error": "Invalid parameters: provide start_time OR end_time."}

    

def get_random_flashcard() -> dict:
    """
    Fetch one random flashcard from the Notion 'Flashcards' database.
    Returns a dict with 'Front' and 'Back' text fields.
    """
    try:
        # Get data source for Flashcards DB
        db_meta = notion.databases.retrieve(DB_FLASHCARDS)
        data_source_id = db_meta["data_sources"][0]["id"]

        # Query a batch of flashcards (you can adjust page_size if your DB is large)
        res = notion.request(
            path=f"/data_sources/{data_source_id}/query",
            method="POST",
            body={"page_size": 20}
        )

        pages = res.get("results", [])
        if not pages:
            return {"error": "No flashcards found"}

        # Pick one at random
        card = random.choice(pages)
        props = card.get("properties", {})

        print(props)

        front = ""
        back = ""

        # Extract 'Front' (title)
        if "Front" in props and props["Front"].get("title"):
            front = props["Front"]["title"][0]["text"]["content"]

        # Extract 'Back' (rich_text)
        if "Back" in props and props["Back"].get("rich_text"):
            back = props["Back"]["rich_text"][0]["text"]["content"]

        return {"Front": front, "Back": back}

    except Exception as e:
        return {"error": str(e)}
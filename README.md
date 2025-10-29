# Notion Language Lab

Assistant to learn languages :
- Flashcards
- Study Timer (start/stop)
- Connexion to Notion (Flashcards / Sessions)

## Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # state NOTION_TOKEN Notion IDs
uvicorn app.main:app --reload --port 8000

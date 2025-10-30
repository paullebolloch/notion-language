# 🧠 Notion Language API

A lightweight FastAPI service that connects with a Notion database to manage and review language flashcards using the **Leitner spaced repetition system**.

---

## 🚀 Features
- Fetch flashcards by language with a frequency inversely proportional to their Leitner level — the higher the number of consecutive successes, the lower the review frequency (https://en.wikipedia.org/wiki/Leitner_system)
- Update flashcard stats (Leitner level, repetition count, date)
- Synchronize directly with your Notion database
- Deployable on **Google Cloud Run** using Docker
- Secure environment variable management

---

## 🧩 Tech Stack
- **Python 3.11**
- **FastAPI**
- **Notion SDK**
- **Docker**
- **Google Cloud Run** + **Artifact Registry**

---

## ⚙️ Setup

### 1️⃣ Environment Variables
Create a `.env` file in the project root:
```bash
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
### 2️⃣ Run Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### 3️⃣ Deploy to Cloud Run
```bash
gcloud run deploy notion-language \
  --source . \
  --region=europe-west1
```

---

### 🧠 Example Usage
Get a random flashcard
```bash
curl "https://notion-language-xxxxxx.a.run.app/flashcards/random?language=Spanish"
```
Update flashcard stats
```bash
curl -X POST "https://notion-language-xxxxxx.a.run.app/flashcards/update?id=page123&success=true"
```
---

### 🧱 Project Structure
```bash
notion-language/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── notion.py      # Notion API helpers
│   └── config.py           # For environment variables
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```
---

### 🔒 Security
- No secrets are stored in GitHub.
- .env is excluded via .gitignore.
- Environment variables are injected via Cloud Run interface.
- The API can be restricted via IAM for private access.

---

### 👤 Author
Paul Le Bolloch
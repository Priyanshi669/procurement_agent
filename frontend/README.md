# Procurement Agent — Streamlit Frontend

Chat UI for the FastAPI backend in `main.py`.

## Setup

```bash
cd frontend
pip install -r requirements.txt
```

## Run

1. Start the API from the project root:

   ```bash
   uvicorn main:app --reload
   ```

2. Start the frontend:

   ```bash
   streamlit run app.py
   ```

Optional: point at a different API host with `API_URL`:

```bash
API_URL=http://localhost:8000 streamlit run app.py
```

## API endpoints used

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Connection check |
| `POST` | `/chat` | Send a message (`session_id`, `message`) |
| `POST` | `/reset/{session_id}` | Clear server-side session state |

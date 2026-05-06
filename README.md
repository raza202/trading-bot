# Trading Bot Skeleton

## Backend (FastAPI)

- Entry point: `backend/app/main.py`
- Run:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Routes:
- `GET /health`
- `GET /stocks` (dummy list of 10 PSX stocks)

## Frontend

- Static dashboard: `frontend/index.html`
- Open directly in browser.

No trading logic included in this phase.

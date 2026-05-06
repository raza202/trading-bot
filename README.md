# Trading Bot Skeleton

## Backend (FastAPI)

- Entry point: `backend/app/main.py`

### Local run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Production mode

Set `ENVIRONMENT=production` to disable API docs endpoints (`/docs`, `/redoc`, `/openapi.json`).

### Routes

- `GET /health`
- `GET /stocks`
- `GET /stock/{symbol}`
- `GET /signals`
- `GET /timeframe/{timeframe}`
- `POST /alerts/email`

### Email alerts

`POST /alerts/email` request body:

```json
{
  "recipient": "user@example.com",
  "symbol": "OGDC"
}
```

Required environment variables:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_SENDER`

Use `backend/.env.example` as the template.

## Deployment (Render)

- Config file: `render.yaml`
- Service uses `uvicorn` with host `0.0.0.0`, port `$PORT`, workers `2`, and health check `/health`.

## Frontend

- Static dashboard: `frontend/index.html`
- Open directly in browser.

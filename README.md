# UK Wind Forecast Decision Portal

Pilot web app for a UK energy utility’s **day-ahead procurement** team. It shows the **national wind forecast available at decision time** (Elexon WINDFOR) and **quantified forecast error** versus **outturn** (Elexon FUELHH, `fuelType=WIND`) for **January 2026**.

## Live links

| Resource | URL |
|----------|-----|
| Frontend (Render static — public) | https://kjhwrx7qm-web.onrender.com |
| Frontend (Vercel) | https://kjhwrx7qm.vercel.app |
| Backend API (Render Docker) | https://kjhwrx7qm-api.onrender.com |
| Backend API (Render Python, backup) | https://kjhwrx7qm-pyapi.onrender.com |
| GitHub repo | https://github.com/Vija047/Gridbricks |
| Demo video (YouTube, unlisted) | _add after recording — see `docs/VIDEO_SCRIPT.md`_ |

API health: `GET /health` · OpenAPI docs: `GET /docs`

**Note:** Prefer the Render static frontend for anonymous / incognito review. If Vercel asks for login, disable Deployment Protection in the Vercel project settings (SSO protection is on by default on some accounts). Render free-tier APIs may cold-start for ~30–60s after idle.

## What it does

1. **Decision forecasts** — For each delivery day D in January 2026, select the latest WINDFOR publish with `publishTime ≤ 11:00 Europe/London on D−1`, aligned to 48 half-hour settlement periods.
2. **Accuracy** — MAE, RMSE, MAPE, and bias of those decision forecasts vs FUELHH wind outturn (latest publish per interval).

### Domain assumptions

- **Decision cutoff** defaults to `11:00` `Europe/London` on D−1 (configurable via env).
- **Actuals**: latest `publishTime` per `startTime` from FUELHH WIND.
- **Resolution**: FUELHH is half-hourly; WINDFOR is often hourly — hourly MW is assigned to both half-hours in that hour when a 30‑minute point is missing.

## Tech stack

- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Backend:** Python, FastAPI, Pydantic, HTTPX, Pandas, SQLite
- **Ops:** Docker Compose; Vercel (UI) + Render (API)

## Repository layout

```text
/
├── README.md
├── docker-compose.yml
├── render.yaml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/                 # FastAPI application
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/routes/      # health, meta, forecasts, actuals, accuracy
│   │   ├── clients/elexon.py
│   │   ├── services/        # normalize, selection, metrics, store
│   │   └── models/schemas.py
│   ├── scripts/sync_january_2026.py
│   └── data/
│       ├── wind_jan2026.db  # local DB (gitignored)
│       └── seed/            # committed slim seed for demos
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/pages/           # Dashboard, Decision, Accuracy
│   └── src/components/
└── docs/VIDEO_SCRIPT.md
```

## Quick start (Docker)

```bash
# From repo root
docker compose up --build
```

- UI: http://localhost:8080  
- API: http://localhost:8000/health  

Seed data loads automatically if the local DB is empty.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Optional: refresh from Elexon (writes DB + seed)
python scripts/sync_january_2026.py

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
# Point at local API
set VITE_API_URL=http://localhost:8000   # Windows PowerShell: $env:VITE_API_URL="http://localhost:8000"
npm run dev
```

Open http://localhost:5173

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/api/v1/meta` | Scope, cutoff, coverage |
| GET | `/api/v1/forecasts/decision?delivery_date=2026-01-15` | Decision curve + optional actuals |
| GET | `/api/v1/actuals?from=2026-01-01&to=2026-01-31` | Outturn series |
| GET | `/api/v1/accuracy/summary` | Month + daily metrics |
| GET | `/api/v1/accuracy/series?delivery_date=2026-01-15` | Half-hourly errors |

## Environment

See [`.env.example`](.env.example).

| Variable | Role |
|----------|------|
| `VITE_API_URL` | Frontend → backend base URL (build-time for Vite) |
| `CORS_ORIGINS` | Allowed browser origins (comma-separated) |
| `DECISION_CUTOFF_LOCAL_TIME` | Default `11:00` |
| `DECISION_TIMEZONE` | Default `Europe/London` |
| `DATABASE_PATH` | SQLite path (default `data/wind_jan2026.db`) |

## Deploy

### Render (backend)

1. Connect this repo; use `render.yaml` or Docker root `backend/`.
2. Health check: `/health`.
3. Seed DB is included under `backend/data/seed/` and copied on first boot.

### Vercel (frontend)

1. Root directory: `frontend`
2. Build: `npm run build` · Output: `dist`
3. Env: `VITE_API_URL=https://<your-render-service>.onrender.com`

## AI tools disclosure

This project was built with assistance from **Cursor** (AI coding agent) for scaffolding, Elexon integration, metrics, UI components, Docker/deploy config, and documentation. All domain logic, APIs, and deliverables were reviewed and validated against live Elexon data for January 2026.

## License

Assignment / pilot use. Data © Elexon / BMRS; used via the public Insights API.

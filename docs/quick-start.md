# Quick Start

This guide gets CTEM Leader Lab running locally.

## Prerequisites

- Python 3.9 or newer
- Node.js 20 or newer
- npm

## Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

Useful endpoints:

- `GET /api/program-summary`
- `GET /api/business-services`
- `GET /api/prioritized-exposures`
- `GET /api/attack-paths`
- `GET /api/remediation-actions`

## Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

If your API uses a different port:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

If the backend is not running, the frontend falls back to static demo data in `frontend/public/api`. This keeps the GitHub Pages demo usable as a read-only scenario walkthrough.

## Verify

```bash
cd backend
pytest
```

```bash
cd frontend
npm run lint
npm run build
```

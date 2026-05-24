# Quick Start

## Using Docker (recommended)

See the [main README](../README.md#using-docker-recommended) for one-command setup with Docker Compose. The default Compose setup exposes only the frontend on `http://localhost:8080`; the backend stays on the internal Docker network.

## Manual Development Setup

### Prerequisites

- Python 3.9 or newer
- Node.js 20 or newer
- npm

### Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. To require a local token for CSV imports, reset, and session mutations, start it with:

```bash
export CTEM_ADMIN_TOKEN=change-me-for-local-live-mode
uvicorn main:app --reload
```

The token is a local safety gate, not enterprise authentication.

Useful endpoints:

- `GET /api/program-summary`
- `GET /api/business-services`
- `GET /api/prioritized-exposures`
- `GET /api/attack-paths`
- `GET /api/remediation-actions`

### Start the Frontend

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

### Verify

```bash
cd backend
pytest
```

```bash
cd frontend
npm run lint
npm run build
```

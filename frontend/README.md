# CTEM Leader Lab Frontend

Interactive React/Vite workbench for security leaders learning how to implement Continuous Threat Exposure Management.

The app is intentionally scenario-driven for the MVP. It does not connect to scanners, ticketing systems, cloud accounts, or identity platforms yet. The frontend consumes the local FastAPI API and presents a guided leader workflow across the five CTEM stages:

- Scoping: business services, crown jewels, owners, and risk appetite.
- Discovery: normalized exposures across CVEs, cloud, identity, secrets, SaaS, and control gaps.
- Prioritization: CTEM decisions that combine business impact, threat signals, exploit likelihood, reachability, identity/control weakness, validation evidence, and remediation feasibility.
- Validation: safe attack-path evidence and control-performance checks.
- Mobilization: owners, SLAs, RACI, retest, exceptions, and a 30/60/90-day roadmap.

## Local Run

Start the backend first from `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then start the frontend from `frontend/`:

```bash
npm install
npm run dev
```

The frontend defaults to `http://localhost:8000` for the API. Override it with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Verification

```bash
npm run lint
npm run build
```

Backend checks live in `backend/test_*.py` and can be run from the backend directory:

```bash
pytest
```

## Framing References

This project uses public CTEM concepts and related prioritization practices from Gartner CTEM stages, FIRST EPSS, CISA Known Exploited Vulnerabilities, CISA SSVC, and MITRE ATT&CK. The product framing is intentionally broader than vulnerability management: it is about validated exposure reduction against crown-jewel business services.

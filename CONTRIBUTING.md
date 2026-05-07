# Contributing to CTEM Leader Lab

Thanks for helping make CTEM easier to understand and implement.

## Good Contributions

We especially welcome:

- Better CTEM operating-model guidance for CISOs and security directors.
- More realistic fictional exposure scenarios.
- Improvements to scoring transparency and leader rationale.
- Documentation, workshop prompts, diagrams, and templates.
- Test coverage for backend scoring and API behavior.
- Frontend fixes that improve clarity, accessibility, and responsiveness.

## Safety Boundaries

CTEM Leader Lab is a learning workbench, not an exploitation framework. Contributions must not add:

- Real exploit automation.
- Instructions for unauthorized testing.
- Secrets, real customer data, or sensitive internal details.
- Claims that cannot be explained or evidenced.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run build
```

## Pull Request Checklist

- Explain the user-facing value of the change.
- Keep fictional data realistic but clearly fictional.
- Update docs when behavior, scoring, or workflows change.
- Add or update tests when changing backend logic.
- Run backend tests and frontend lint/build before submitting.

## Content Style

- Write for security leaders first, practitioners second.
- Prefer plain language over tool jargon.
- Explain why a CTEM decision changes action.
- Distinguish traditional vulnerability management from CTEM without straw-manning either.

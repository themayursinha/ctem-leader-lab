<p align="center">
  <img src="./assets/ctem-hero.svg" alt="CTEM Leader Lab" width="920">
</p>

<h1 align="center">CTEM Leader Lab</h1>

<p align="center">
  An interactive implementation workbench for security leaders moving from vulnerability management to Continuous Threat Exposure Management.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#why-ctem">Why CTEM</a> ·
  <a href="#leader-workflows">Leader Workflows</a> ·
  <a href="#scoring-model">Scoring Model</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="./docs/workshop-guide.md">Workshop Guide</a>
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-v0.4.0-00d084">
  <a href="https://github.com/themayursinha/ctem-leader-lab/actions/workflows/ci.yml">
    <img alt="CI" src="https://github.com/themayursinha/ctem-leader-lab/actions/workflows/ci.yml/badge.svg">
  </a>
  <img alt="Backend" src="https://img.shields.io/badge/backend-FastAPI-009688">
  <img alt="Frontend" src="https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb">
  <img alt="CTEM" src="https://img.shields.io/badge/CTEM-Leader%20Lab-00d084">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

<p align="center">
  <a href="https://themayursinha.github.io/ctem-leader-lab/">Live Demo</a> ·
  <a href="./docs/quick-start.md">Local Setup</a> ·
  <a href="./CHANGELOG.md">Release Notes</a>
</p>

---

## Why CTEM

Traditional vulnerability management often asks: **Which CVEs are severe enough to patch first?**

Continuous Threat Exposure Management asks: **Which validated exposure paths create the most credible business risk, and who will reduce them?**

CTEM Leader Lab is a fictional, scenario-driven product for CISOs, security directors, and security program owners. It teaches how to scope crown-jewel services, discover exposures across domains, prioritize by business and threat context, validate attack paths safely, and mobilize remediation with accountable owners.

This is not a scanner. It is a leadership workbench for learning the CTEM operating model.

## Quick Start

### Using Docker (recommended)

[Install Docker](https://docs.docker.com/get-docker/), then run a single command:

```bash
make up
```

Or without `make`:

```bash
docker compose up --build -d
```

Open **http://localhost:8080**. The app loads with realistic demo data, and all features (CSV import/export, sessions, executive summary) work immediately.

To stop:

```bash
make down
# or: docker compose down
```

### Manual development setup

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Static demo (no backend needed)

The frontend includes pre-baked JSON data under `frontend/public/api/`, so the GitHub Pages build works entirely without a running backend. Some features (CSV import/export, sessions, reset) require a live backend.

## Screenshots

### Executive Dashboard

![CTEM Leader Lab dashboard](./assets/screenshots/dashboard.png)

### Prioritization

![CTEM prioritization workflow](./assets/screenshots/prioritization.png)

### Validation

![CTEM validation workflow](./assets/screenshots/validation.png)

### Mobilization

![CTEM mobilization workflow](./assets/screenshots/mobilization.png)

## What Makes It Different

- **Business-first scoping:** Starts with critical services, crown-jewel assets, owners, and risk appetite.
- **Exposure, not vulnerability, inventory:** Models CVEs, cloud misconfigurations, identity weaknesses, leaked secrets, SaaS posture, and control gaps.
- **Transparent CTEM scoring:** Combines business criticality, reachability, known exploitation, EPSS-style likelihood, identity/control weakness, attack-path proximity, remediation feasibility, and evidence confidence.
- **Validation evidence:** Connects prioritization to safe attack-path evidence, blast radius, and control-performance checks.
- **Mobilization:** Turns validated exposure into owner, SLA, RACI, retest, exception, and executive escalation workflows.

## Leader Workflows

| Stage | Leader question | Output |
| --- | --- | --- |
| Scoping | Which business services deserve scarce remediation capacity first? | Crown-jewel worksheet and scoped asset map |
| Discovery | What exposures exist across technology, identity, cloud, SaaS, and controls? | Normalized exposure inventory |
| Prioritization | Which exposures create the most credible path to business harm? | Act, Attend, Monitor, or Track decisions |
| Validation | What evidence proves exploitability, reachability, or control failure? | Attack-path evidence pack |
| Mobilization | Who will fix, accept, retest, or escalate the risk? | Remediation board, RACI, and 30/60/90 plan |

## Scoring Model

The MVP uses realistic seeded data and a transparent decision engine. It intentionally lets a medium-severity identity or secret exposure outrank an isolated high-CVSS issue when validation shows a stronger path to a crown-jewel business service.

Decision outcomes:

- **Act:** Validated or high-confidence path to business harm. Mobilize immediately.
- **Attend:** Important scoped exposure that needs leadership-backed coordination.
- **Monitor:** Real issue, but current evidence does not justify urgent mobilization.
- **Track:** Handle through normal hygiene unless threat or reachability changes.

Read more in [docs/scoring-model.md](./docs/scoring-model.md).

## Features

- **Five CTEM stages** — Navigate Scoping, Discovery, Prioritization, Validation, and Mobilization with realistic seed data.
- **CSV import/export** — Export assets, exposures, and remediation actions; import changes with validation and error reporting.
- **Workshop sessions** — Save and load named snapshots of the full workspace state.
- **Executive summary** — Download a Markdown or HTML report of the current program state.
- **Workshop Pack** — Generate a facilitator-ready takeaway with templates, remediation board snapshot, and 30/60/90-day roadmap.
- **Docker one-command startup** — `make up` or `docker compose up --build -d`.
- **User Guide & Glossary** — In-app reference explaining CTEM concepts, EPSS, KEV, CTEM score, and more.
- **Toast notifications** — Transient success/error feedback for all import/export/session actions.
- **Search & sort** — Filter and sort tables in Scoping and Discovery views.
- **Maturity chart** — Visual bar chart of program maturity domains on the dashboard.
- **Skeleton loading** — Shimmer placeholders while data loads.
- **Accessible** — Skip-to-content, hamburger menu on mobile, ARIA labels, and keyboard-friendly navigation.

## Project Structure

```text
backend/         FastAPI API, seeded CTEM scenario data, scoring engine, tests
frontend/        React/Vite leader workbench UI
docs/            Operating model, quick start, scoring model, workshop guide
assets/          README and project visuals
.github/         CI workflow and contribution templates
docker-compose.yml   Docker one-command startup
Makefile             make up / down / build / test / logs
.env.example         Documented environment variables
```

## Verification

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Roadmap

- ~~`v0.1.0`: Scenario-driven CTEM Leader Lab MVP.~~
- ~~`v0.2.0`: CSV import/export for assets, exposures, and remediation actions.~~
- ~~`v0.3.0`: Saved workshop sessions and exportable executive summary.~~
- ~~`v0.4.0`: Docker, onboarding, UX polish, error handling, accessibility.~~
- `v0.5.0`: Optional integrations for scanner, cloud, identity, and ticketing data.

## Contributing

Contributions are welcome when they improve the leader learning experience, CTEM operating model, data realism, scoring transparency, documentation, or test coverage. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Security

This project contains fictional seed data and is not an offensive testing tool. Do not use it to test systems you do not own or have permission to assess. See [SECURITY.md](./SECURITY.md).

## License

MIT. See [LICENSE](./LICENSE).

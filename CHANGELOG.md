# Changelog

All notable changes to CTEM Leader Lab are documented here.

## v0.4.0 — Production Readiness

### CSV Import/Export (v0.2.0)
- Added 7 new backend endpoints for CSV import/export of assets, exposures, and remediation actions.
- Sanitized streaming CSV export with injection guards.
- All-or-nothing Pydantic validation with per-row error reporting.
- 10 MB / 10 000 row upload limits with MIME type checks.
- Thread-safe in-place data mutations.
- Added `CsvToolbar` component with export, import, and reset buttons.
- Exposed in Scoping, Discovery, and Mobilization views (hidden in static mode).

### SQLite Persistence & Workshop Sessions (v0.3.0)
- Added `backend/db.py` — SQLite persistence layer with WAL mode, parameterized queries, and threading lock.
- DataStore persists after every mutation and loads from DB on startup.
- `current_state` table for live data, `sessions` table for named snapshots.
- 5 session endpoints: save, list, get, load, delete.
- Executive summary endpoint returning Markdown or HTML.
- Sessions frontend view with save/load/delete and executive summary download.
- 9 new backend tests (27 total, all passing).

### Docker One-Command Startup (Phase 1)
- `docker-compose.yml` with backend (uvicorn) and frontend (nginx) services.
- Multi-stage frontend Dockerfile (node:22-alpine build → nginx:alpine serve).
- Nginx proxies `/api/` to backend; same-origin API calls.
- Named Docker volume `ctem-data` for SQLite persistence across restarts.
- `Makefile` with `up`/`down`/`build`/`test`/`logs` targets.
- `.env.example` documenting all environment variables.
- CORS origins configurable via `CORS_ORIGINS` env var.
- `VITE_API_LIVE` build-time flag with relative URL fallback.
- README updated with Docker quick-start as primary method.

### Onboarding & Comprehension (Phase 2)
- Welcome modal on first visit with app overview and feature highlights.
- Dismissable demo data banner (amber) notifying users the data is fictional.
- Tooltip component with CSS hover tooltips on KEV, EPSS, CTEM score, crown jewel, decision badges, exposure type, source severity, and internet reachability.
- User Guide page at `/guide` with Overview, Five CTEM Stages, Key Features, and Glossary (EPSS, KEV, CVSS, attack path, RACI, SLA, etc.).

### UX Polish (Phase 3)
- Skeleton loading states (shimmer animation) replacing text spinners across all 7 views.
- recharts bar chart on Dashboard showing maturity domain scores.
- TableSearch component enabling search/filter on Scoping and Discovery tables.
- Sortable table columns with visual asc/desc indicators.
- Clickable table rows with hover highlight.
- Breadcrumbs component on all sub-pages.
- Toast notification system (`ToastProvider` + `useToast`) with success/error types.
- CSV template download button per entity type.

### Error Handling & Resilience (Phase 4)
- ErrorBoundary component catching render crashes with friendly fallback UI.
- ConfirmDialog modal replacing `window.confirm` for destructive actions.
- User-friendly error messages with hidden technical error details.
- Static mode notices in Scoping, Discovery, and Mobilization explaining why CSV features are hidden.

### Accessibility & Mobile (Phase 5)
- Skip-to-content link (hidden until focused) for keyboard users.
- Hamburger menu on mobile (< 1100 px) that toggles a slide-in sidebar with backdrop overlay.
- Focus management on route change (main content area receives focus).
- `aria-label` on sidebar nav, tables, search inputs, sortable headers, CSV toolbar buttons, and session action buttons.
- `aria-sort` on sortable table columns, `aria-current="page"` on active sidebar links, `aria-expanded` on hamburger button, `aria-modal` on welcome dialog.
- Welcome dialog traps focus on open.

## v0.1.0 — CTEM Leader Lab MVP

- Added FastAPI read-only APIs for program summary, maturity, services, assets, exposures, prioritized exposures, attack paths, remediation actions, and workshop artifacts.
- Added fictional but realistic CTEM scenario data.
- Added static demo API JSON for GitHub Pages hosting.
- Added transparent CTEM scoring with Act, Attend, Monitor, and Track outcomes.
- Rebuilt the React UI around dashboard, scoping, discovery, prioritization, validation, and mobilization workflows.
- Added backend tests for scoring, API serialization, and seeded data relationships.
- Added project README, screenshots, docs, community files, CI workflow, and Pages deployment foundation.

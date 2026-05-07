# Scoring Model

The MVP scoring model is intentionally transparent. It is designed for education and decision clarity, not for statistical prediction.

## Inputs

Each exposure is scored using:

- Business criticality
- Internet exposure and reachability
- Known exploited signal
- EPSS-style exploit likelihood
- Identity or privilege amplification
- Preventive or detective control weakness
- Attack-path proximity to crown jewels
- Remediation feasibility
- Evidence confidence

## Decision Outcomes

| Outcome | Meaning | Typical mobilization |
| --- | --- | --- |
| Act | Validated or high-confidence path to business harm | Immediate owner assignment and short SLA |
| Attend | Important scoped exposure needing coordination | Leadership-backed remediation plan |
| Monitor | Real exposure without urgent validated path | Watch for threat, reachability, or evidence changes |
| Track | Hygiene issue for normal maintenance | Standard backlog or accepted risk path |

## Why This Matters

The model intentionally allows a medium-severity leaked secret or identity weakness to outrank an isolated high-CVSS issue. CTEM should protect remediation capacity for the exposure paths most likely to create business harm.

## Current Implementation

The backend implementation lives in `backend/scoring.py`.

Tests assert that:

- The leaked CI token outranks the isolated engineering wiki CVE.
- Prioritized exposures include rationale, evidence, owner, SLA, and next action.
- Decision thresholds remain stable.

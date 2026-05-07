from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data import (
    ASSETS,
    ATTACK_PATHS,
    BUSINESS_SERVICES,
    EXPOSURES,
    MATURITY,
    REMEDIATION_ACTIONS,
    WORKSHOP_ARTIFACTS,
)
from models import (
    Asset,
    AttackPath,
    BusinessService,
    Exposure,
    MaturityDomain,
    PrioritizedExposure,
    ProgramSummary,
    RemediationAction,
    WorkshopArtifacts,
)
from scoring import prioritized_exposures


app = FastAPI(title="CTEM Leader Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/program-summary", response_model=ProgramSummary)
def get_program_summary():
    prioritized = prioritized_exposures()
    act_count = len([item for item in prioritized if item.decision == "Act"])
    attend_count = len([item for item in prioritized if item.decision == "Attend"])
    scoped_services = [service for service in BUSINESS_SERVICES if service.in_scope]
    validated_paths = [path for path in ATTACK_PATHS if path.status == "Validated"]

    return ProgramSummary(
        organization="Northstar Financial Services",
        goal="Move from vulnerability backlog management to validated exposure reduction for crown-jewel services.",
        maturity_current=round(sum(domain.score for domain in MATURITY) / len(MATURITY), 1),
        maturity_target=round(sum(domain.target for domain in MATURITY) / len(MATURITY), 1),
        metrics={
            "scoped_services": len(scoped_services),
            "crown_jewel_assets": len([asset for asset in ASSETS if asset.crown_jewel]),
            "raw_exposures": len(EXPOSURES),
            "act_decisions": act_count,
            "attend_decisions": attend_count,
            "validated_attack_paths": len(validated_paths),
            "sla_at_risk": 2,
            "exposure_reduction_goal": "35% validated critical-path reduction in 90 days",
        },
        operating_principles=[
            "Scope starts with business services and crown jewels, not scanner coverage.",
            "Prioritization explains why an exposure matters and what evidence supports action.",
            "Validation proves exploitability, reachability, control performance, and blast radius safely.",
            "Mobilization assigns accountable owners, SLAs, retest criteria, and exception paths.",
        ],
        cycle=[
            {"stage": "Scoping", "leader_question": "Which business services deserve scarce remediation capacity first?"},
            {"stage": "Discovery", "leader_question": "What exposures exist across technology, identity, cloud, SaaS, and controls?"},
            {"stage": "Prioritization", "leader_question": "Which exposures create the most credible path to business harm?"},
            {"stage": "Validation", "leader_question": "What evidence proves the exposure is exploitable or blocked?"},
            {"stage": "Mobilization", "leader_question": "Who will fix, accept, retest, or escalate the risk?"},
        ],
    )


@app.get("/api/maturity", response_model=list[MaturityDomain])
def get_maturity():
    return MATURITY


@app.get("/api/business-services", response_model=list[BusinessService])
def get_business_services():
    return BUSINESS_SERVICES


@app.get("/api/assets", response_model=list[Asset])
def get_assets():
    return ASSETS


@app.get("/api/exposures", response_model=list[Exposure])
def get_exposures():
    return EXPOSURES


@app.get("/api/prioritized-exposures", response_model=list[PrioritizedExposure])
def get_prioritized_exposures():
    return prioritized_exposures()


@app.get("/api/prioritization", response_model=list[PrioritizedExposure])
def get_legacy_prioritization_alias():
    return prioritized_exposures()


@app.get("/api/attack-paths", response_model=list[AttackPath])
def get_attack_paths():
    return ATTACK_PATHS


@app.get("/api/remediation-actions", response_model=list[RemediationAction])
def get_remediation_actions():
    return REMEDIATION_ACTIONS


@app.get("/api/workshop-artifacts", response_model=WorkshopArtifacts)
def get_workshop_artifacts():
    return WORKSHOP_ARTIFACTS

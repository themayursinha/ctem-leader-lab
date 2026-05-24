from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


Criticality = Literal["Low", "Medium", "High", "Critical"]
Decision = Literal["Track", "Monitor", "Attend", "Act"]
Effort = Literal["Low", "Medium", "High"]
EvidenceConfidence = Literal["Low", "Medium", "High"]
ExposureType = Literal["CVE", "Cloud", "Identity", "Secret", "SaaS", "Control Gap"]
Reachability = Literal["Direct", "Indirect", "Isolated"]
AttackPathStatus = Literal["Validated", "Plausible", "Blocked"]
RemediationStatus = Literal["To Do", "In Progress", "Done", "Accepted Risk"]
RetestStatus = Literal["Not Started", "Scheduled", "Passed", "Blocked"]


class BusinessService(AppBaseModel):
    id: str
    name: str
    description: str
    executive_owner: str
    business_owner: str
    criticality: Criticality
    risk_appetite: str
    customer_impact: str
    revenue_dependency: str
    crown_jewel_asset_ids: list[str]
    in_scope: bool
    scope_reason: str


class Asset(AppBaseModel):
    id: str
    name: str
    type: str
    service_id: str
    owner: str
    environment: str
    criticality: Criticality
    crown_jewel: bool
    internet_exposed: bool
    reachable_from_internet: Reachability
    tags: list[str]


class Exposure(AppBaseModel):
    id: str
    title: str
    description: str
    exposure_type: ExposureType
    asset_id: str
    severity: Criticality
    cvss: Optional[float] = None
    epss_probability: float
    kev_signal: bool
    ransomware_observed: bool
    identity_risk: int
    control_gap: int
    attack_path_proximity: Literal["Crown Jewel", "Same Service", "Adjacent", "None"]
    remediation_effort: Effort
    evidence_confidence: EvidenceConfidence
    evidence: str
    suggested_action: str
    source: Optional[str] = None
    source_reference: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    validated_at: Optional[str] = None
    evidence_owner: Optional[str] = None
    evidence_expires_at: Optional[str] = None


class ScoreDriver(AppBaseModel):
    name: str
    value: int
    explanation: str


class PrioritizedExposure(AppBaseModel):
    exposure_id: str
    asset_id: str
    service_id: str
    title: str
    description: str
    exposure_type: str
    severity: Criticality
    decision: Decision
    ctem_score: int
    rationale: str
    why_it_matters: str
    next_action: str
    score_drivers: list[ScoreDriver]
    validation_evidence: str
    owner: str
    sla: str
    source: Optional[str] = None
    source_reference: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    validated_at: Optional[str] = None
    evidence_owner: Optional[str] = None
    evidence_expires_at: Optional[str] = None


class AttackPathStep(AppBaseModel):
    order: int
    title: str
    asset_id: str
    technique: str
    validation: str
    control_gap: str


class AttackPath(AppBaseModel):
    id: str
    name: str
    objective: str
    business_service_id: str
    exposure_ids: list[str]
    status: AttackPathStatus
    evidence_confidence: EvidenceConfidence
    blast_radius: str
    safe_validation_method: str
    steps: list[AttackPathStep]


class RemediationAction(AppBaseModel):
    id: str
    exposure_id: str
    title: str
    owner: str
    team: str
    status: RemediationStatus
    priority: Decision
    sla: str
    due_in_days: int
    playbook: str
    dependency: str
    retest_status: RetestStatus
    risk_acceptance_required: bool


class MaturityDomain(AppBaseModel):
    name: str
    score: int
    target: int
    current_state: str
    next_step: str


class ProgramSummary(AppBaseModel):
    organization: str
    goal: str
    maturity_current: float
    maturity_target: float
    metrics: dict[str, Any]
    operating_principles: list[str]
    cycle: list[dict[str, str]]


class WorkshopArtifacts(AppBaseModel):
    maturity_assessment: list[str]
    crown_jewel_worksheet: list[str]
    prioritization_rationale: list[str]
    validation_evidence_pack: list[str]
    raci: list[dict[str, str]]
    roadmap_30_60_90: list[dict[str, str]]


class AuditEvent(AppBaseModel):
    id: str
    created_at: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    summary: str
    metadata: dict[str, Any]

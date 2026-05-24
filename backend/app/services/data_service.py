import uuid
from copy import deepcopy
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.scoring import score_exposure, decision_for_score, rationale_for, why_it_matters
from app.db.models import (
    AssetModel,
    AttackPathModel,
    AttackPathStepModel,
    AuditEventModel,
    BusinessServiceModel,
    ExposureModel,
    MaturityDomainModel,
    OrganizationModel,
    RemediationActionModel,
    SessionModel,
)
from app.db.repositories.asset_repo import AssetRepository
from app.db.repositories.audit_repo import AuditRepository
from app.db.repositories.exposure_repo import ExposureRepository
from app.db.repositories.remediation_repo import RemediationRepository
from app.db.repositories.session_repo import SessionRepository
from app.models.domain import (
    Asset,
    AttackPath,
    AttackPathStep,
    AuditEvent,
    BusinessService,
    Exposure,
    MaturityDomain,
    PrioritizedExposure,
    ProgramSummary,
    RemediationAction,
    WorkshopArtifacts,
)
from app.seed import data as seed_data


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class DataService:
    def __init__(self, db: Session):
        self._db = db
        self._asset_repo = AssetRepository(db)
        self._exposure_repo = ExposureRepository(db)
        self._remediation_repo = RemediationRepository(db)
        self._session_repo = SessionRepository(db)
        self._audit_repo = AuditRepository(db)

    def _seed_if_empty(self) -> None:
        if self._db.query(BusinessServiceModel).count() > 0:
            return
        self._seed_all()

    def _seed_all(self) -> None:
        org = self._db.query(OrganizationModel).first()
        if not org:
            org = OrganizationModel(name="Northstar Financial Services")
            self._db.add(org)
            self._db.flush()
        for bs in seed_data.BUSINESS_SERVICES:
            self._db.add(BusinessServiceModel(**bs.model_dump(), organization_id=org.id))
        for a in seed_data.ASSETS:
            self._db.add(AssetModel(**a.model_dump()))
        for e in seed_data.EXPOSURES:
            self._db.add(ExposureModel(**e.model_dump()))
        for ap in seed_data.ATTACK_PATHS:
            ap_dict = ap.model_dump(exclude={"steps"})
            ap_model = AttackPathModel(**ap_dict)
            for step in ap.steps:
                ap_model.steps.append(AttackPathStepModel(
                    attack_path_id=ap.id,
                    order=step.order,
                    title=step.title,
                    asset_id=step.asset_id,
                    technique=step.technique,
                    validation=step.validation,
                    control_gap=step.control_gap,
                ))
            self._db.add(ap_model)
        for m in seed_data.MATURITY:
            self._db.add(MaturityDomainModel(name=m.name, score=m.score, target=m.target,
                                             current_state=m.current_state, next_step=m.next_step))
        for r in seed_data.REMEDIATION_ACTIONS:
            self._db.add(RemediationActionModel(**r.model_dump()))
        self._db.commit()

    # --- Business services ---

    def get_business_services(self) -> list[BusinessService]:
        self._seed_if_empty()
        return [BusinessService.model_validate(bs) for bs in self._db.query(BusinessServiceModel).all()]

    # --- Assets ---

    def get_assets(self) -> list[Asset]:
        self._seed_if_empty()
        return [Asset.model_validate(a) for a in self._asset_repo.all()]

    def replace_assets(self, new_assets: list[Asset]) -> None:
        self._asset_repo.delete_all()
        for a in new_assets:
            self._db.add(AssetModel(**a.model_dump()))
        self._db.commit()

    # --- Exposures ---

    def get_exposures(self) -> list[Exposure]:
        self._seed_if_empty()
        return [Exposure.model_validate(e) for e in self._exposure_repo.all()]

    def replace_exposures(self, new_exposures: list[Exposure]) -> None:
        self._exposure_repo.delete_all()
        for e in new_exposures:
            self._db.add(ExposureModel(**e.model_dump()))
        self._db.commit()

    # --- Remediation actions ---

    def get_remediation_actions(self) -> list[RemediationAction]:
        self._seed_if_empty()
        return [RemediationAction.model_validate(r) for r in self._remediation_repo.all()]

    def replace_remediation_actions(self, new_actions: list[RemediationAction]) -> None:
        self._remediation_repo.delete_all()
        for r in new_actions:
            self._db.add(RemediationActionModel(**r.model_dump()))
        self._db.commit()

    # --- Attack paths ---

    def get_attack_paths(self) -> list[AttackPath]:
        self._seed_if_empty()
        models = self._db.query(AttackPathModel).all()
        result = []
        for ap in models:
            steps = [{
                "order": s.order,
                "title": s.title,
                "asset_id": s.asset_id,
                "technique": s.technique,
                "validation": s.validation,
                "control_gap": s.control_gap,
            } for s in sorted(ap.steps, key=lambda s: s.order)]
            ap_dict = {c.name: getattr(ap, c.name) for c in AttackPathModel.__table__.columns}
            ap_dict.pop("id", None)
            result.append(AttackPath(
                id=ap.id,
                name=ap.name,
                objective=ap.objective,
                business_service_id=ap.business_service_id,
                exposure_ids=ap.exposure_ids or [],
                status=ap.status,
                evidence_confidence=ap.evidence_confidence,
                blast_radius=ap.blast_radius,
                safe_validation_method=ap.safe_validation_method,
                steps=[AttackPathStep(**s) for s in steps],
            ))
        return result

    # --- Maturity ---

    def get_maturity(self) -> list[MaturityDomain]:
        self._seed_if_empty()
        return [MaturityDomain.model_validate(m) for m in self._db.query(MaturityDomainModel).all()]

    # --- Prioritization ---

    def get_prioritized_exposures(self) -> list[PrioritizedExposure]:
        exposures = self.get_exposures()
        assets_map = {a.id: a for a in self.get_assets()}
        services_map = {bs.id: bs.name for bs in self.get_business_services()}
        remediation_map = {r.exposure_id: r.sla for r in self.get_remediation_actions()}

        prioritized = []
        for exposure in exposures:
            asset = assets_map[exposure.asset_id]
            service_name = services_map[asset.service_id]
            score, drivers = score_exposure(exposure, asset)
            decision = decision_for_score(score)

            prioritized.append(PrioritizedExposure(
                exposure_id=exposure.id,
                asset_id=asset.id,
                service_id=asset.service_id,
                title=exposure.title,
                description=exposure.description,
                exposure_type=exposure.exposure_type,
                severity=exposure.severity,
                decision=decision,
                ctem_score=score,
                rationale=rationale_for(exposure, asset, decision, service_name),
                why_it_matters=why_it_matters(exposure, asset, service_name),
                next_action=exposure.suggested_action,
                score_drivers=drivers,
                validation_evidence=exposure.evidence,
                owner=asset.owner,
                sla=remediation_map.get(exposure.id, "Not assigned"),
                source=exposure.source,
                source_reference=exposure.source_reference,
                first_seen=exposure.first_seen,
                last_seen=exposure.last_seen,
                validated_at=exposure.validated_at,
                evidence_owner=exposure.evidence_owner,
                evidence_expires_at=exposure.evidence_expires_at,
            ))

        return sorted(prioritized, key=lambda item: item.ctem_score, reverse=True)

    # --- Program summary ---

    def get_program_summary(self) -> ProgramSummary:
        prioritized = self.get_prioritized_exposures()
        services = self.get_business_services()
        assets = self.get_assets()
        maturity = self.get_maturity()
        attack_paths = self.get_attack_paths()

        act_count = len([p for p in prioritized if p.decision == "Act"])
        attend_count = len([p for p in prioritized if p.decision == "Attend"])
        scoped_services = [s for s in services if s.in_scope]
        validated_paths = [p for p in attack_paths if p.status == "Validated"]

        return ProgramSummary(
            organization="Northstar Financial Services",
            goal="Move from vulnerability backlog management to validated exposure reduction for crown-jewel services.",
            maturity_current=round(sum(d.score for d in maturity) / len(maturity), 1),
            maturity_target=round(sum(d.target for d in maturity) / len(maturity), 1),
            metrics={
                "scoped_services": len(scoped_services),
                "crown_jewel_assets": len([a for a in assets if a.crown_jewel]),
                "raw_exposures": len(self.get_exposures()),
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

    # --- Workshop artifacts ---

    def get_workshop_artifacts(self) -> WorkshopArtifacts:
        return deepcopy(seed_data.WORKSHOP_ARTIFACTS)

    # --- Reset ---

    def reset(self) -> None:
        self._db.query(RemediationActionModel).delete()
        self._db.query(ExposureModel).delete()
        self._db.query(AssetModel).delete()
        self._db.query(AttackPathStepModel).delete()
        self._db.query(AttackPathModel).delete()
        self._db.query(MaturityDomainModel).delete()
        self._db.query(BusinessServiceModel).delete()
        self._db.commit()
        self._seed_all()

    # --- Sessions ---

    def save_session(self, name: str) -> str:
        session_id = str(uuid.uuid4())
        now = _iso_now()
        assets = [a.model_dump(mode="json") for a in self.get_assets()]
        exposures = [e.model_dump(mode="json") for e in self.get_exposures()]
        remediation = [r.model_dump(mode="json") for r in self.get_remediation_actions()]
        self._db.add(SessionModel(
            id=session_id, name=name, created_at=now, updated_at=now,
            assets=assets, exposures=exposures, remediation_actions=remediation,
        ))
        self._db.commit()
        return session_id

    def list_sessions(self) -> list[dict]:
        return self._session_repo.list_all()

    def get_session_info(self, session_id: str) -> dict | None:
        s = self._session_repo.get(session_id)
        if s is None:
            return None
        return {"id": s.id, "name": s.name, "created_at": s.created_at, "updated_at": s.updated_at}

    def load_session(self, session_id: str) -> bool:
        s = self._session_repo.get_full(session_id)
        if s is None:
            return False
        self._db.query(RemediationActionModel).delete()
        self._db.query(ExposureModel).delete()
        self._db.query(AttackPathStepModel).delete()
        self._db.query(AttackPathModel).delete()
        self._db.query(AssetModel).delete()
        self._db.commit()
        for a_data in s.assets:
            self._db.add(AssetModel(**a_data))
        for e_data in s.exposures:
            self._db.add(ExposureModel(**e_data))
        for r_data in s.remediation_actions:
            self._db.add(RemediationActionModel(**r_data))
        self._db.commit()
        return True

    def delete_session(self, session_id: str) -> bool:
        return self._session_repo.delete(session_id)

    # --- Audit ---

    def record_audit_event(self, action: str, resource_type: str, resource_id: str | None,
                           summary: str, metadata: dict | None = None) -> str:
        event_id = str(uuid.uuid4())
        now = _iso_now()
        self._db.add(AuditEventModel(
            id=event_id, created_at=now, action=action, resource_type=resource_type,
            resource_id=resource_id, summary=summary, details=metadata or {},
        ))
        self._db.commit()
        return event_id

    def list_audit_events(self, limit: int = 100) -> list[AuditEvent]:
        return self._audit_repo.list_recent(limit=limit)

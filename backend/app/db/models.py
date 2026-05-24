import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class BusinessServiceModel(Base):
    __tablename__ = "business_services"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    executive_owner = Column(String(200), nullable=False)
    business_owner = Column(String(200), nullable=False)
    criticality = Column(String(20), nullable=False)
    risk_appetite = Column(Text, nullable=False)
    customer_impact = Column(Text, nullable=False)
    revenue_dependency = Column(String(200), nullable=False)
    crown_jewel_asset_ids = Column(JSON, nullable=False, default=list)
    in_scope = Column(Boolean, nullable=False, default=False)
    scope_reason = Column(Text, nullable=False, default="")

    assets = relationship("AssetModel", back_populates="service", cascade="all, delete-orphan")
    attack_paths = relationship("AttackPathModel", back_populates="service", cascade="all, delete-orphan")


class AssetModel(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=False)
    service_id = Column(String, ForeignKey("business_services.id"), nullable=False, index=True)
    owner = Column(String(200), nullable=False)
    environment = Column(String(100), nullable=False)
    criticality = Column(String(20), nullable=False)
    crown_jewel = Column(Boolean, nullable=False, default=False)
    internet_exposed = Column(Boolean, nullable=False, default=False)
    reachable_from_internet = Column(String(20), nullable=False)
    tags = Column(JSON, nullable=False, default=list)

    service = relationship("BusinessServiceModel", back_populates="assets")
    exposures = relationship("ExposureModel", back_populates="asset", cascade="all, delete-orphan")
    attack_path_steps = relationship("AttackPathStepModel", back_populates="asset", cascade="all, delete-orphan")


class ExposureModel(Base):
    __tablename__ = "exposures"

    id = Column(String, primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    exposure_type = Column(String(30), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    cvss = Column(Float, nullable=True)
    epss_probability = Column(Float, nullable=False, default=0.0)
    kev_signal = Column(Boolean, nullable=False, default=False)
    ransomware_observed = Column(Boolean, nullable=False, default=False)
    identity_risk = Column(Integer, nullable=False, default=0)
    control_gap = Column(Integer, nullable=False, default=0)
    attack_path_proximity = Column(String(30), nullable=False)
    remediation_effort = Column(String(10), nullable=False)
    evidence_confidence = Column(String(10), nullable=False)
    evidence = Column(Text, nullable=False, default="")
    suggested_action = Column(Text, nullable=False, default="")
    source = Column(String(200), nullable=True)
    source_reference = Column(String(200), nullable=True)
    first_seen = Column(String(30), nullable=True)
    last_seen = Column(String(30), nullable=True)
    validated_at = Column(String(30), nullable=True)
    evidence_owner = Column(String(200), nullable=True)
    evidence_expires_at = Column(String(30), nullable=True)

    asset = relationship("AssetModel", back_populates="exposures")
    remediation_actions = relationship("RemediationActionModel", back_populates="exposure", cascade="all, delete-orphan")


class RemediationActionModel(Base):
    __tablename__ = "remediation_actions"

    id = Column(String, primary_key=True)
    exposure_id = Column(String, ForeignKey("exposures.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    owner = Column(String(200), nullable=False)
    team = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False)
    priority = Column(String(10), nullable=False)
    sla = Column(String(50), nullable=False)
    due_in_days = Column(Integer, nullable=False, default=0)
    playbook = Column(Text, nullable=False, default="")
    dependency = Column(String(300), nullable=False, default="")
    retest_status = Column(String(20), nullable=False)
    risk_acceptance_required = Column(Boolean, nullable=False, default=False)

    exposure = relationship("ExposureModel", back_populates="remediation_actions")


class AttackPathModel(Base):
    __tablename__ = "attack_paths"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    objective = Column(Text, nullable=False)
    business_service_id = Column(String, ForeignKey("business_services.id"), nullable=False, index=True)
    exposure_ids = Column(JSON, nullable=False, default=list)
    status = Column(String(20), nullable=False)
    evidence_confidence = Column(String(10), nullable=False)
    blast_radius = Column(Text, nullable=False)
    safe_validation_method = Column(Text, nullable=False)

    service = relationship("BusinessServiceModel", back_populates="attack_paths")
    steps = relationship("AttackPathStepModel", back_populates="attack_path", cascade="all, delete-orphan")


class AttackPathStepModel(Base):
    __tablename__ = "attack_path_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attack_path_id = Column(String, ForeignKey("attack_paths.id"), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    technique = Column(String(200), nullable=False)
    validation = Column(Text, nullable=False)
    control_gap = Column(Text, nullable=False)

    attack_path = relationship("AttackPathModel", back_populates="steps")
    asset = relationship("AssetModel", back_populates="attack_path_steps")


class MaturityDomainModel(Base):
    __tablename__ = "maturity_domains"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
    target = Column(Integer, nullable=False)
    current_state = Column(Text, nullable=False)
    next_step = Column(Text, nullable=False)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)
    assets = Column(JSON, nullable=False)
    exposures = Column(JSON, nullable=False)
    remediation_actions = Column(JSON, nullable=False)


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True)
    created_at = Column(String(30), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String, nullable=True)
    summary = Column(Text, nullable=False)
    details = Column("metadata", JSON, nullable=False, default=dict)

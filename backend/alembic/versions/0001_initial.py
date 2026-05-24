"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(length=30), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "business_services",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("executive_owner", sa.String(length=200), nullable=False),
        sa.Column("business_owner", sa.String(length=200), nullable=False),
        sa.Column("criticality", sa.String(length=20), nullable=False),
        sa.Column("risk_appetite", sa.Text(), nullable=False),
        sa.Column("customer_impact", sa.Text(), nullable=False),
        sa.Column("revenue_dependency", sa.String(length=200), nullable=False),
        sa.Column("crown_jewel_asset_ids", sa.JSON(), nullable=False),
        sa.Column("in_scope", sa.Boolean(), nullable=False),
        sa.Column("scope_reason", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "maturity_domains",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("target", sa.Integer(), nullable=False),
        sa.Column("current_state", sa.Text(), nullable=False),
        sa.Column("next_step", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.String(length=30), nullable=False),
        sa.Column("updated_at", sa.String(length=30), nullable=False),
        sa.Column("assets", sa.JSON(), nullable=False),
        sa.Column("exposures", sa.JSON(), nullable=False),
        sa.Column("remediation_actions", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("service_id", sa.String(), nullable=False),
        sa.Column("owner", sa.String(length=200), nullable=False),
        sa.Column("environment", sa.String(length=100), nullable=False),
        sa.Column("criticality", sa.String(length=20), nullable=False),
        sa.Column("crown_jewel", sa.Boolean(), nullable=False),
        sa.Column("internet_exposed", sa.Boolean(), nullable=False),
        sa.Column("reachable_from_internet", sa.String(length=20), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["business_services.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assets_service_id"), "assets", ["service_id"], unique=False)
    op.create_table(
        "attack_paths",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("business_service_id", sa.String(), nullable=False),
        sa.Column("exposure_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("evidence_confidence", sa.String(length=10), nullable=False),
        sa.Column("blast_radius", sa.Text(), nullable=False),
        sa.Column("safe_validation_method", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["business_service_id"], ["business_services.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attack_paths_business_service_id"), "attack_paths", ["business_service_id"], unique=False)
    op.create_table(
        "exposures",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("exposure_type", sa.String(length=30), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("cvss", sa.Float(), nullable=True),
        sa.Column("epss_probability", sa.Float(), nullable=False),
        sa.Column("kev_signal", sa.Boolean(), nullable=False),
        sa.Column("ransomware_observed", sa.Boolean(), nullable=False),
        sa.Column("identity_risk", sa.Integer(), nullable=False),
        sa.Column("control_gap", sa.Integer(), nullable=False),
        sa.Column("attack_path_proximity", sa.String(length=30), nullable=False),
        sa.Column("remediation_effort", sa.String(length=10), nullable=False),
        sa.Column("evidence_confidence", sa.String(length=10), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("source_reference", sa.String(length=200), nullable=True),
        sa.Column("first_seen", sa.String(length=30), nullable=True),
        sa.Column("last_seen", sa.String(length=30), nullable=True),
        sa.Column("validated_at", sa.String(length=30), nullable=True),
        sa.Column("evidence_owner", sa.String(length=200), nullable=True),
        sa.Column("evidence_expires_at", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exposures_asset_id"), "exposures", ["asset_id"], unique=False)
    op.create_table(
        "attack_path_steps",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("attack_path_id", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("technique", sa.String(length=200), nullable=False),
        sa.Column("validation", sa.Text(), nullable=False),
        sa.Column("control_gap", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ),
        sa.ForeignKeyConstraint(["attack_path_id"], ["attack_paths.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attack_path_steps_attack_path_id"), "attack_path_steps", ["attack_path_id"], unique=False)
    op.create_table(
        "remediation_actions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exposure_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("owner", sa.String(length=200), nullable=False),
        sa.Column("team", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("sla", sa.String(length=50), nullable=False),
        sa.Column("due_in_days", sa.Integer(), nullable=False),
        sa.Column("playbook", sa.Text(), nullable=False),
        sa.Column("dependency", sa.String(length=300), nullable=False),
        sa.Column("retest_status", sa.String(length=20), nullable=False),
        sa.Column("risk_acceptance_required", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["exposure_id"], ["exposures.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_remediation_actions_exposure_id"), "remediation_actions", ["exposure_id"], unique=False)


def downgrade() -> None:
    op.drop_table("remediation_actions")
    op.drop_table("attack_path_steps")
    op.drop_table("exposures")
    op.drop_table("attack_paths")
    op.drop_table("assets")
    op.drop_table("sessions")
    op.drop_table("maturity_domains")
    op.drop_table("business_services")
    op.drop_table("audit_events")

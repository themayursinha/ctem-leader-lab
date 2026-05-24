"""add organizations and users tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_organization_id"), "users", ["organization_id"], unique=False)
    op.add_column("business_services", sa.Column("organization_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_business_services_organization_id"), "business_services", ["organization_id"], unique=False)
    op.create_foreign_key("fk_business_services_org", "business_services", "organizations",
                          ["organization_id"], ["organizations"]["id"])


def downgrade() -> None:
    op.drop_constraint("fk_business_services_org", "business_services", type_="foreignkey")
    op.drop_index(op.f("ix_business_services_organization_id"), table_name="business_services")
    op.drop_column("business_services", "organization_id")
    op.drop_index(op.f("ix_users_organization_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")

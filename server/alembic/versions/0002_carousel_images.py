"""add carousel_images table

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-21

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "carousel_images",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(128), server_default="", nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("carousel_images")
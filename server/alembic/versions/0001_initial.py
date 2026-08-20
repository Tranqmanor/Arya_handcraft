"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-18

对应 preplan.md 第 5 节数据模型。
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("openid", sa.String(64), nullable=False),
        sa.Column("unionid", sa.String(64), nullable=True),
        sa.Column("nickname", sa.String(64), server_default="", nullable=False),
        sa.Column("avatar_url", sa.Text(), server_default="", nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("openid"),
        sa.UniqueConstraint("unionid"),
        sa.UniqueConstraint("phone"),
    )

    op.create_table(
        "coupons",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("status", sa.String(16), server_default="unused", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_coupons_user", "coupons", ["user_id", "status"])

    op.create_table(
        "videos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("video_url", sa.Text(), nullable=False),
        sa.Column("cover_url", sa.Text(), server_default="", nullable=False),
        sa.Column("duration", sa.Integer(), server_default="0", nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "video_views",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("video_id", sa.BigInteger(), sa.ForeignKey("videos.id"), nullable=False),
        sa.Column("viewer_key", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("video_id", "viewer_key", name="uq_video_views"),
    )
    op.create_index("idx_video_views_video", "video_views", ["video_id"])

    op.create_table(
        "articles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("summary", sa.String(256), server_default="", nullable=False),
        sa.Column("cover_url", sa.Text(), server_default="", nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), server_default="general", nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ai_messages_user", "ai_messages", ["user_id", "created_at"])

    op.create_table(
        "admin_users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    op.drop_table("admin_users")
    op.drop_table("ai_messages")
    op.drop_table("articles")
    op.drop_table("video_views")
    op.drop_table("videos")
    op.drop_table("coupons")
    op.drop_table("users")

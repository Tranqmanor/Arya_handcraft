"""add orders / addresses / payment_records / home_settings, extend users

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "addresses",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("receiver", sa.String(64), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("region", sa.String(128), server_default="", nullable=False),
        sa.Column("detail", sa.Text(), server_default="", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("order_no", sa.String(32), nullable=False, unique=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("referrer_user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("cat_name", sa.String(64), server_default="", nullable=False),
        sa.Column("requirement", sa.Text(), server_default="", nullable=False),
        sa.Column("images", sa.JSON(), nullable=False),
        sa.Column("address_snapshot", sa.JSON(), nullable=False),
        sa.Column("total_price", sa.Integer(), nullable=True),
        sa.Column("coupon_id", sa.BigInteger(), sa.ForeignKey("coupons.id"), nullable=True),
        sa.Column("coupon_amount", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(24), server_default="pending_price", nullable=False, index=True),
        sa.Column("deposit_due", sa.Integer(), server_default="0", nullable=False),
        sa.Column("making_due", sa.Integer(), server_default="0", nullable=False),
        sa.Column("final_due", sa.Integer(), server_default="0", nullable=False),
        sa.Column("paid_deposit", sa.Integer(), server_default="0", nullable=False),
        sa.Column("paid_making", sa.Integer(), server_default="0", nullable=False),
        sa.Column("paid_final", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cover_image_url", sa.String(), server_default="", nullable=False),
        sa.Column("making_photos", sa.JSON(), nullable=False),
        sa.Column("shipping_company", sa.String(64), server_default="", nullable=False),
        sa.Column("tracking_no", sa.String(64), server_default="", nullable=False),
        sa.Column("price_note", sa.String(255), server_default="", nullable=False),
        sa.Column("refund_reason", sa.String(255), server_default="", nullable=False),
        sa.Column("refund_amount", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cancel_reason", sa.String(255), server_default="", nullable=False),
        sa.Column("deposit_paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("making_paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("final_paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "payment_records",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("order_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("stage", sa.String(16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(16), server_default="manual", nullable=False),
        sa.Column("note", sa.String(255), server_default="", nullable=False),
        sa.Column("operator_admin_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "home_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("promo_image_url", sa.String(), server_default="", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.add_column("users", sa.Column("cat_name", sa.String(64), server_default="", nullable=False))
    op.add_column("users", sa.Column("referrer_user_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "referrer_user_id")
    op.drop_column("users", "cat_name")
    op.drop_table("home_settings")
    op.drop_table("payment_records")
    op.drop_table("orders")
    op.drop_table("addresses")
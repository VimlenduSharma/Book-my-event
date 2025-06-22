"""Initial schema

Creates tables: event, slot, booking, review
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# ——— revision identifiers ———————————————————————————————
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None
# ————————————————————————————————————————————————————————————


def upgrade() -> None:
    # ——— EVENT --------------------------------------------------------------
    op.create_table(
        "event",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("host_name", sa.String(), nullable=False, index=True),
        sa.Column("category", sa.String(), nullable=False, index=True),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("price_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("rating_avg", sa.Numeric(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR()
            if op.get_context().dialect.name == "postgresql"
            else sa.Text(),
            nullable=True,
        ),
    )

    # ——— SLOT  --------------------------------------------------------------
    op.create_table(
        "slot",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_id", sa.String(), sa.ForeignKey("event.id"), nullable=False),
        sa.Column("start_utc", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("max_bookings", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("event_id", "start_utc", name="uix_event_start"),
    )

    # ——— BOOKING ------------------------------------------------------------
    op.create_table(
        "booking",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("slot_id", sa.String(), sa.ForeignKey("slot.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, index=True),
        sa.Column(
            "status",
            sa.Enum("CONFIRMED", "CANCELLED", name="bookingstatus"),
            nullable=False,
            server_default="CONFIRMED",
        ),
        sa.Column("booked_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slot_id", "email", name="uix_slot_email"),
    )

    # ——— REVIEW -------------------------------------------------------------
    op.create_table(
        "review",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_id", sa.String(), sa.ForeignKey("event.id"), nullable=False),
        sa.Column("booking_id", sa.String(), sa.ForeignKey("booking.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Optional: indices for faster look-ups
    op.create_index("ix_event_created_at", "event", ["created_at"])
    op.create_index("ix_slot_start", "slot", ["start_utc"])


def downgrade() -> None:
    op.drop_index("ix_slot_start", table_name="slot")
    op.drop_index("ix_event_created_at", table_name="event")
    op.drop_table("review")
    op.drop_table("booking")
    op.drop_table("slot")
    op.drop_table("event")

"""furniture catalog table

Revision ID: 0002_catalog
Revises: 0001_plot
Create Date: 2026-07-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_catalog"
down_revision: Union[str, Sequence[str], None] = "0001_plot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED_ITEMS = [
    ("Sofa",            "seating", 2.2, 0.85, 0.9,  "#6b7280", 799.0,  "3-seat fabric sofa"),
    ("Armchair",        "seating", 0.9, 0.85, 0.9,  "#78716c", 349.0,  "Upholstered armchair"),
    ("Dining Table",    "tables",  1.8, 0.75, 0.9,  "#8b5e3c", 599.0,  "6-seat dining table"),
    ("Dining Chair",    "seating", 0.45, 0.9, 0.5,  "#a8785a", 89.0,   "Wooden dining chair"),
    ("Queen Bed",       "bedroom", 1.6, 0.6,  2.1,  "#9ca3af", 899.0,  "Queen-size bed frame"),
    ("Wardrobe",        "storage", 1.2, 2.0,  0.6,  "#57534e", 649.0,  "2-door wardrobe"),
    ("Bookshelf",       "storage", 0.9, 1.8,  0.35, "#78716c", 199.0,  "5-shelf bookcase"),
    ("Coffee Table",    "tables",  1.1, 0.4,  0.6,  "#8b5e3c", 149.0,  "Low coffee table"),
    ("TV Unit",         "storage", 1.6, 0.5,  0.4,  "#44403c", 279.0,  "TV console/media unit"),
    ("Kitchen Island",  "tables",  1.5, 0.9,  0.8,  "#a3a3a3", 1299.0, "Freestanding kitchen island"),
]


def upgrade() -> None:
    op.create_table(
        "furniture_catalog",
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("depth", sa.Float(), nullable=False),
        sa.Column("default_color", sa.String(9), nullable=False, server_default="#8b5e3c"),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        schema="plot_unified",
    )
    op.create_index("ix_catalog_category", "furniture_catalog", ["category"], schema="plot_unified")

    catalog_table = sa.table(
        "furniture_catalog",
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("width", sa.Float),
        sa.column("height", sa.Float),
        sa.column("depth", sa.Float),
        sa.column("default_color", sa.String),
        sa.column("price", sa.Float),
        sa.column("description", sa.String),
        schema="plot_unified",
    )
    op.bulk_insert(
        catalog_table,
        [
            {
                "name": name, "category": category,
                "width": w, "height": h, "depth": d,
                "default_color": color, "price": price, "description": desc,
            }
            for name, category, w, h, d, color, price, desc in _SEED_ITEMS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_catalog_category", table_name="furniture_catalog", schema="plot_unified")
    op.drop_table("furniture_catalog", schema="plot_unified")

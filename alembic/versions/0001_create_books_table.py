"""create books table

Revision ID: 0001
Revises:
Create Date: 2026-06-10

Создаёт таблицу books (соответствует модели data/models/book.py).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("author", sa.String(length=300), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("genre", sa.String(length=100), nullable=False),
        sa.Column("pages", sa.Integer(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("isbn", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("book_id"),
    )
    op.create_index(op.f("ix_books_book_id"), "books", ["book_id"], unique=False)
    op.create_index(op.f("ix_books_title"), "books", ["title"], unique=False)
    op.create_index(op.f("ix_books_author"), "books", ["author"], unique=False)
    op.create_index(op.f("ix_books_year"), "books", ["year"], unique=False)
    op.create_index(op.f("ix_books_genre"), "books", ["genre"], unique=False)
    op.create_index(op.f("ix_books_available"), "books", ["available"], unique=False)
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.drop_index(op.f("ix_books_available"), table_name="books")
    op.drop_index(op.f("ix_books_genre"), table_name="books")
    op.drop_index(op.f("ix_books_year"), table_name="books")
    op.drop_index(op.f("ix_books_author"), table_name="books")
    op.drop_index(op.f("ix_books_title"), table_name="books")
    op.drop_index(op.f("ix_books_book_id"), table_name="books")
    op.drop_table("books")
